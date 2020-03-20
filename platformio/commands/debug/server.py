# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
from os.path import isdir, isfile, join

from twisted.internet import defer  # pylint: disable=import-error
from twisted.internet import reactor  # pylint: disable=import-error

from platformio import fs, util
from platformio.commands.debug.exception import DebugInvalidOptionsError
from platformio.commands.debug.helpers import escape_gdbmi_stream, is_gdbmi_mode
from platformio.commands.debug.process import BaseProcess
from platformio.proc import where_is_program


class DebugServer(BaseProcess):
    def __init__(self, debug_options, env_options):
        super(DebugServer, self).__init__()
        self.debug_options = debug_options
        self.env_options = env_options

        self._debug_port = ":3333"
        self._transport = None
        self._process_ended = False
        self._ready = False

    @defer.inlineCallbacks
    def spawn(self, patterns):  # pylint: disable=too-many-branches
        systype = util.get_systype()
        server = self.debug_options.get("server")
        if not server:
            defer.returnValue(None)
        server = self.apply_patterns(server, patterns)
        server_executable = server["executable"]
        if not server_executable:
            defer.returnValue(None)
        if server["cwd"]:
            server_executable = join(server["cwd"], server_executable)
        if (
            "windows" in systype
            and not server_executable.endswith(".exe")
            and isfile(server_executable + ".exe")
        ):
            server_executable = server_executable + ".exe"

        if not isfile(server_executable):
            server_executable = where_is_program(server_executable)
        if not isfile(server_executable):
            raise DebugInvalidOptionsError(
                "\nCould not launch Debug Server '%s'. Please check that it "
                "is installed and is included in a system PATH\n\n"
                "See documentation or contact contact@platformio.org:\n"
                "https://docs.platformio.org/page/plus/debugging.html\n"
                % server_executable
            )

        openocd_pipe_allowed = all(
            [not self.debug_options["port"], "openocd" in server_executable]
        )
        if openocd_pipe_allowed:
            args = []
            if server["cwd"]:
                args.extend(["-s", server["cwd"]])
            args.extend(
                ["-c", "gdb_port pipe; tcl_port disabled; telnet_port disabled"]
            )
            args.extend(server["arguments"])
            str_args = " ".join(
                [arg if arg.startswith("-") else '"%s"' % arg for arg in args]
            )
            self._debug_port = '| "%s" %s' % (server_executable, str_args)
            self._debug_port = fs.to_unix_path(self._debug_port)
            defer.returnValue(self._debug_port)

        env = os.environ.copy()
        # prepend server "lib" folder to LD path
        if (
            "windows" not in systype
            and server["cwd"]
            and isdir(join(server["cwd"], "lib"))
        ):
            ld_key = "DYLD_LIBRARY_PATH" if "darwin" in systype else "LD_LIBRARY_PATH"
            env[ld_key] = join(server["cwd"], "lib")
            if os.environ.get(ld_key):
                env[ld_key] = "%s:%s" % (env[ld_key], os.environ.get(ld_key))
        # prepend BIN to PATH
        if server["cwd"] and isdir(join(server["cwd"], "bin")):
            env["PATH"] = "%s%s%s" % (
                join(server["cwd"], "bin"),
                os.pathsep,
                os.environ.get("PATH", os.environ.get("Path", "")),
            )

        self._transport = reactor.spawnProcess(
            self,
            server_executable,
            [server_executable] + server["arguments"],
            path=server["cwd"],
            env=env,
        )
        if "mspdebug" in server_executable.lower():
            self._debug_port = ":2000"
        elif "jlink" in server_executable.lower():
            self._debug_port = ":2331"
        elif "qemu" in server_executable.lower():
            self._debug_port = ":1234"

        yield self._wait_until_ready()

        defer.returnValue(self._debug_port)

    @defer.inlineCallbacks
    def _wait_until_ready(self):
        timeout = 10
        elapsed = 0
        delay = 0.5
        auto_ready_delay = 0.5
        while not self._ready and not self._process_ended and elapsed < timeout:
            yield self.async_sleep(delay)
            if not self.debug_options.get("server", {}).get("ready_pattern"):
                self._ready = self._last_activity < (time.time() - auto_ready_delay)
            elapsed += delay

    @staticmethod
    def async_sleep(secs):
        d = defer.Deferred()
        reactor.callLater(secs, d.callback, None)
        return d

    def get_debug_port(self):
        return self._debug_port

    def outReceived(self, data):
        super(DebugServer, self).outReceived(
            escape_gdbmi_stream("@", data) if is_gdbmi_mode() else data
        )
        if self._ready:
            return
        ready_pattern = self.debug_options.get("server", {}).get("ready_pattern")
        if ready_pattern:
            self._ready = ready_pattern.encode() in data

    def processEnded(self, reason):
        self._process_ended = True
        super(DebugServer, self).processEnded(reason)

    def terminate(self):
        if self._process_ended or not self._transport:
            return
        try:
            self._transport.signalProcess("KILL")
        except:  # pylint: disable=bare-except
            pass
