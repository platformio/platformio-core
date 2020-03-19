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
import re
import signal
import time
from hashlib import sha1
from os.path import basename, dirname, isdir, join, realpath, splitext
from tempfile import mkdtemp

from twisted.internet import defer  # pylint: disable=import-error
from twisted.internet import protocol  # pylint: disable=import-error
from twisted.internet import reactor  # pylint: disable=import-error
from twisted.internet import stdio  # pylint: disable=import-error
from twisted.internet import task  # pylint: disable=import-error

from platformio import app, fs, proc, telemetry, util
from platformio.commands.debug import helpers
from platformio.commands.debug.exception import DebugInvalidOptionsError
from platformio.commands.debug.initcfgs import get_gdb_init_config
from platformio.commands.debug.process import BaseProcess
from platformio.commands.debug.server import DebugServer
from platformio.compat import hashlib_encode_data, is_bytes
from platformio.project.helpers import get_project_cache_dir


class GDBClient(BaseProcess):  # pylint: disable=too-many-instance-attributes

    PIO_SRC_NAME = ".pioinit"
    INIT_COMPLETED_BANNER = "PlatformIO: Initialization completed"

    def __init__(self, project_dir, args, debug_options, env_options):
        super(GDBClient, self).__init__()
        self.project_dir = project_dir
        self.args = list(args)
        self.debug_options = debug_options
        self.env_options = env_options

        self._debug_server = DebugServer(debug_options, env_options)
        self._session_id = None

        if not isdir(get_project_cache_dir()):
            os.makedirs(get_project_cache_dir())
        self._gdbsrc_dir = mkdtemp(dir=get_project_cache_dir(), prefix=".piodebug-")

        self._target_is_run = False
        self._auto_continue_timer = None
        self._errors_buffer = b""

    @defer.inlineCallbacks
    def spawn(self, gdb_path, prog_path):
        session_hash = gdb_path + prog_path
        self._session_id = sha1(hashlib_encode_data(session_hash)).hexdigest()
        self._kill_previous_session()

        patterns = {
            "PROJECT_DIR": self.project_dir,
            "PROG_PATH": prog_path,
            "PROG_DIR": dirname(prog_path),
            "PROG_NAME": basename(splitext(prog_path)[0]),
            "DEBUG_PORT": self.debug_options["port"],
            "UPLOAD_PROTOCOL": self.debug_options["upload_protocol"],
            "INIT_BREAK": self.debug_options["init_break"] or "",
            "LOAD_CMDS": "\n".join(self.debug_options["load_cmds"] or []),
        }

        yield self._debug_server.spawn(patterns)
        if not patterns["DEBUG_PORT"]:
            patterns["DEBUG_PORT"] = self._debug_server.get_debug_port()

        self.generate_pioinit(self._gdbsrc_dir, patterns)

        # start GDB client
        args = [
            "piogdb",
            "-q",
            "--directory",
            self._gdbsrc_dir,
            "--directory",
            self.project_dir,
            "-l",
            "10",
        ]
        args.extend(self.args)
        if not gdb_path:
            raise DebugInvalidOptionsError("GDB client is not configured")
        gdb_data_dir = self._get_data_dir(gdb_path)
        if gdb_data_dir:
            args.extend(["--data-directory", gdb_data_dir])
        args.append(patterns["PROG_PATH"])

        transport = reactor.spawnProcess(
            self, gdb_path, args, path=self.project_dir, env=os.environ
        )
        defer.returnValue(transport)

    @staticmethod
    def _get_data_dir(gdb_path):
        if "msp430" in gdb_path:
            return None
        gdb_data_dir = realpath(join(dirname(gdb_path), "..", "share", "gdb"))
        return gdb_data_dir if isdir(gdb_data_dir) else None

    def generate_pioinit(self, dst_dir, patterns):
        # default GDB init commands depending on debug tool
        commands = get_gdb_init_config(self.debug_options).split("\n")

        if self.debug_options["init_cmds"]:
            commands = self.debug_options["init_cmds"]
        commands.extend(self.debug_options["extra_cmds"])

        if not any("define pio_reset_run_target" in cmd for cmd in commands):
            commands = [
                "define pio_reset_run_target",
                "   echo Warning! Undefined pio_reset_run_target command\\n",
                "   monitor reset",
                "end",
            ] + commands
        if not any("define pio_reset_halt_target" in cmd for cmd in commands):
            commands = [
                "define pio_reset_halt_target",
                "   echo Warning! Undefined pio_reset_halt_target command\\n",
                "   monitor reset halt",
                "end",
            ] + commands
        if not any("define pio_restart_target" in cmd for cmd in commands):
            commands += [
                "define pio_restart_target",
                "   pio_reset_halt_target",
                "   $INIT_BREAK",
                "   %s" % ("continue" if patterns["INIT_BREAK"] else "next"),
                "end",
            ]

        banner = [
            "echo PlatformIO Unified Debugger -> http://bit.ly/pio-debug\\n",
            "echo PlatformIO: debug_tool = %s\\n" % self.debug_options["tool"],
            "echo PlatformIO: Initializing remote target...\\n",
        ]
        footer = ["echo %s\\n" % self.INIT_COMPLETED_BANNER]
        commands = banner + commands + footer

        with open(join(dst_dir, self.PIO_SRC_NAME), "w") as fp:
            fp.write("\n".join(self.apply_patterns(commands, patterns)))

    def connectionMade(self):
        self._lock_session(self.transport.pid)

        p = protocol.Protocol()
        p.dataReceived = self.onStdInData
        stdio.StandardIO(p)

    def onStdInData(self, data):
        super(GDBClient, self).onStdInData(data)
        if b"-exec-run" in data:
            if self._target_is_run:
                token, _ = data.split(b"-", 1)
                self.outReceived(token + b"^running\n")
                return
            data = data.replace(b"-exec-run", b"-exec-continue")

        if b"-exec-continue" in data:
            self._target_is_run = True
        if b"-gdb-exit" in data or data.strip() in (b"q", b"quit"):
            # Allow terminating via SIGINT/CTRL+C
            signal.signal(signal.SIGINT, signal.default_int_handler)
            self.transport.write(b"pio_reset_run_target\n")
        self.transport.write(data)

    def processEnded(self, reason):  # pylint: disable=unused-argument
        self._unlock_session()
        if self._gdbsrc_dir and isdir(self._gdbsrc_dir):
            fs.rmtree(self._gdbsrc_dir)
        if self._debug_server:
            self._debug_server.terminate()

        reactor.stop()

    def outReceived(self, data):
        super(GDBClient, self).outReceived(data)
        self._handle_error(data)
        # go to init break automatically
        if self.INIT_COMPLETED_BANNER.encode() in data:
            telemetry.send_event(
                "Debug", "Started", telemetry.encode_run_environment(self.env_options)
            )
            self._auto_continue_timer = task.LoopingCall(self._auto_exec_continue)
            self._auto_continue_timer.start(0.1)

    def errReceived(self, data):
        super(GDBClient, self).errReceived(data)
        self._handle_error(data)

    def console_log(self, msg):
        if helpers.is_gdbmi_mode():
            msg = helpers.escape_gdbmi_stream("~", msg)
        self.outReceived(msg if is_bytes(msg) else msg.encode())

    def _auto_exec_continue(self):
        auto_exec_delay = 0.5  # in seconds
        if self._last_activity > (time.time() - auto_exec_delay):
            return
        if self._auto_continue_timer:
            self._auto_continue_timer.stop()
        self._auto_continue_timer = None

        if not self.debug_options["init_break"] or self._target_is_run:
            return
        self.console_log(
            "PlatformIO: Resume the execution to `debug_init_break = %s`\n"
            % self.debug_options["init_break"]
        )
        self.console_log(
            "PlatformIO: More configuration options -> http://bit.ly/pio-debug\n"
        )
        self.transport.write(
            b"0-exec-continue\n" if helpers.is_gdbmi_mode() else b"continue\n"
        )
        self._target_is_run = True

    def _handle_error(self, data):
        self._errors_buffer += data
        if self.PIO_SRC_NAME.encode() not in data or b"Error in sourced" not in data:
            return

        last_erros = self._errors_buffer.decode()
        last_erros = " ".join(reversed(last_erros.split("\n")))
        last_erros = re.sub(r'((~|&)"|\\n\"|\\t)', " ", last_erros, flags=re.M)

        err = "%s -> %s" % (
            telemetry.encode_run_environment(self.env_options),
            last_erros,
        )
        telemetry.send_exception("DebugInitError: %s" % err)
        self.transport.loseConnection()

    def _kill_previous_session(self):
        assert self._session_id
        pid = None
        with app.ContentCache() as cc:
            pid = cc.get(self._session_id)
            cc.delete(self._session_id)
        if not pid:
            return
        if "windows" in util.get_systype():
            kill = ["Taskkill", "/PID", pid, "/F"]
        else:
            kill = ["kill", pid]
        try:
            proc.exec_command(kill)
        except:  # pylint: disable=bare-except
            pass

    def _lock_session(self, pid):
        if not self._session_id:
            return
        with app.ContentCache() as cc:
            cc.set(self._session_id, str(pid), "1h")

    def _unlock_session(self):
        if not self._session_id:
            return
        with app.ContentCache() as cc:
            cc.delete(self._session_id)
