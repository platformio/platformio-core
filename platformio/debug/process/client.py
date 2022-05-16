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

import hashlib
import os
import signal
import tempfile

from platformio import fs, proc
from platformio.cache import ContentCache
from platformio.compat import IS_WINDOWS, hashlib_encode_data
from platformio.debug.process.base import DebugBaseProcess
from platformio.debug.process.server import DebugServerProcess
from platformio.project.helpers import get_project_cache_dir


class DebugClientProcess(DebugBaseProcess):
    def __init__(self, project_dir, debug_config):
        super().__init__()
        self.project_dir = project_dir
        self.debug_config = debug_config

        self._server_process = None
        self._session_id = None

        if not os.path.isdir(get_project_cache_dir()):
            os.makedirs(get_project_cache_dir())
        self.working_dir = tempfile.mkdtemp(
            dir=get_project_cache_dir(), prefix=".piodebug-"
        )

        self._target_is_running = False
        self._errors_buffer = b""

    async def run(self):
        session_hash = (
            self.debug_config.client_executable_path + self.debug_config.program_path
        )
        self._session_id = hashlib.sha1(hashlib_encode_data(session_hash)).hexdigest()
        self._kill_previous_session()

        if self.debug_config.server:
            self._server_process = DebugServerProcess(self.debug_config)
            self.debug_config.port = await self._server_process.run()

    def connection_made(self, transport):
        super().connection_made(transport)
        self._lock_session(transport.get_pid())
        # Disable SIGINT and allow GDB's Ctrl+C interrupt
        signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
        self.connect_stdin_pipe()

    def process_exited(self):
        if self._server_process:
            self._server_process.terminate()
        super().process_exited()

    def close(self):
        self._unlock_session()
        if self.working_dir and os.path.isdir(self.working_dir):
            fs.rmtree(self.working_dir)

    def __del__(self):
        self.close()

    def _kill_previous_session(self):
        assert self._session_id
        pid = None
        with ContentCache() as cc:
            pid = cc.get(self._session_id)
            cc.delete(self._session_id)
        if not pid:
            return
        if IS_WINDOWS:
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
        with ContentCache() as cc:
            cc.set(self._session_id, str(pid), "1h")

    def _unlock_session(self):
        if not self._session_id:
            return
        with ContentCache() as cc:
            cc.delete(self._session_id)
