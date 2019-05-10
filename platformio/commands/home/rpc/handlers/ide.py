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

import time

import jsonrpc  # pylint: disable=import-error
from twisted.internet import defer  # pylint: disable=import-error


class IDERPC(object):

    def __init__(self):
        self._queue = []

    def send_command(self, command, params):
        if not self._queue:
            raise jsonrpc.exceptions.JSONRPCDispatchException(
                code=4005, message="PIO Home IDE agent is not started")
        while self._queue:
            self._queue.pop().callback({
                "id": time.time(),
                "method": command,
                "params": params
            })

    def listen_commands(self):
        self._queue.append(defer.Deferred())
        return self._queue[-1]

    def open_project(self, project_dir):
        return self.send_command("open_project", project_dir)
