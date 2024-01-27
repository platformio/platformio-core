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

import asyncio
import os
import re
import time

from platformio import fs
from platformio.compat import IS_MACOS, IS_WINDOWS
from platformio.debug.exception import DebugInvalidOptionsError
from platformio.debug.helpers import escape_gdbmi_stream, is_gdbmi_mode
from platformio.debug.process.base import DebugBaseProcess
from platformio.proc import where_is_program


class DebugServerProcess(DebugBaseProcess):
    STD_BUFFER_SIZE = 1024

    def __init__(self, debug_config):
        super().__init__()
        self.debug_config = debug_config
        self._ready = False
        self._std_buffer = {"out": b"", "err": b""}

    async def run(self):  # pylint: disable=too-many-branches
        server = self.debug_config.server
        if not server:
            return None
        server_executable = server["executable"]
        if not server_executable:
            return None
        if server["cwd"]:
            server_executable = os.path.join(server["cwd"], server_executable)
        if (
            IS_WINDOWS
            and not server_executable.endswith(".exe")
            and os.path.isfile(server_executable + ".exe")
        ):
            server_executable = server_executable + ".exe"

        if not os.path.isfile(server_executable):
            server_executable = where_is_program(server_executable)
        if not os.path.isfile(server_executable):
            raise DebugInvalidOptionsError(
                "Could not launch Debug Server '%s'. Please check that it "
                "is installed and is included in a system PATH\n"
                "See https://docs.platformio.org/page/plus/debugging.html"
                % server_executable
            )

        openocd_pipe_allowed = all(
            [
                not self.debug_config.env_options.get(
                    "debug_port", self.debug_config.tool_settings.get("port")
                ),
                "gdb" in self.debug_config.client_executable_path,
                "openocd" in server_executable,
            ]
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
            return fs.to_unix_path('| "%s" %s' % (server_executable, str_args))

        env = os.environ.copy()
        # prepend server "lib" folder to LD path
        if (
            not IS_WINDOWS
            and server["cwd"]
            and os.path.isdir(os.path.join(server["cwd"], "lib"))
        ):
            ld_key = "DYLD_LIBRARY_PATH" if IS_MACOS else "LD_LIBRARY_PATH"
            env[ld_key] = os.path.join(server["cwd"], "lib")
            if os.environ.get(ld_key):
                env[ld_key] = "%s:%s" % (env[ld_key], os.environ.get(ld_key))
        # prepend BIN to PATH
        if server["cwd"] and os.path.isdir(os.path.join(server["cwd"], "bin")):
            env["PATH"] = "%s%s%s" % (
                os.path.join(server["cwd"], "bin"),
                os.pathsep,
                os.environ.get("PATH", os.environ.get("Path", "")),
            )

        await self.spawn(
            *([server_executable] + server["arguments"]), cwd=server["cwd"], env=env
        )
        await self._wait_until_ready()

        return self.debug_config.port

    async def _wait_until_ready(self):
        ready_pattern = self.debug_config.server_ready_pattern
        timeout = 60 if ready_pattern else 10
        elapsed = 0
        delay = 0.5
        auto_ready_delay = 0.5
        while not self._ready and self.is_running() and elapsed < timeout:
            await asyncio.sleep(delay)
            if not ready_pattern:
                self._ready = self._last_activity < (time.time() - auto_ready_delay)
            elapsed += delay

    def _check_ready_by_pattern(self, data):
        if self._ready:
            return self._ready
        ready_pattern = self.debug_config.server_ready_pattern
        if ready_pattern:
            if ready_pattern.startswith("^"):
                self._ready = re.match(
                    ready_pattern,
                    data.decode("utf-8", "ignore"),
                )
            else:
                self._ready = ready_pattern.encode() in data
        return self._ready

    def stdout_data_received(self, data):
        super().stdout_data_received(
            escape_gdbmi_stream("@", data) if is_gdbmi_mode() else data
        )
        self._std_buffer["out"] += data
        self._check_ready_by_pattern(self._std_buffer["out"])
        self._std_buffer["out"] = self._std_buffer["out"][-1 * self.STD_BUFFER_SIZE :]

    def stderr_data_received(self, data):
        super().stderr_data_received(data)
        self._std_buffer["err"] += data
        self._check_ready_by_pattern(self._std_buffer["err"])
        self._std_buffer["err"] = self._std_buffer["err"][-1 * self.STD_BUFFER_SIZE :]
