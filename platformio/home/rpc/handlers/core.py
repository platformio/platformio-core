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
import functools

from platformio import __main__, __version__, app, proc, util
from platformio.compat import (
    IS_WINDOWS,
    aio_create_task,
    aio_get_running_loop,
    get_locale_encoding,
)
from platformio.home.rpc.handlers.base import BaseRPCHandler


class PIOCoreProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future, on_data_callback=None):
        self.exit_future = exit_future
        self.on_data_callback = on_data_callback
        self.stdout = ""
        self.stderr = ""
        self._is_exited = False
        self._encoding = get_locale_encoding()

    def pipe_data_received(self, fd, data):
        data = data.decode(self._encoding, "replace")
        pipe = ["stdin", "stdout", "stderr"][fd]
        if pipe == "stdout":
            self.stdout += data
        if pipe == "stderr":
            self.stderr += data
        if self.on_data_callback:
            self.on_data_callback(pipe=pipe, data=data)

    def connection_lost(self, exc):
        self.process_exited()

    def process_exited(self):
        if self._is_exited:
            return
        self.exit_future.set_result(True)
        self._is_exited = True


@util.memoized(expire="60s")
def get_core_fullpath():
    return proc.where_is_program("platformio" + (".exe" if IS_WINDOWS else ""))


class CoreRPC(BaseRPCHandler):
    NAMESPACE = "core"

    @staticmethod
    def version():
        return __version__

    async def exec(self, args, options=None):
        loop = aio_get_running_loop()
        exit_future = loop.create_future()
        data_callback = functools.partial(
            self._on_exec_data_received, exec_options=options
        )
        if args[0] != "--caller" and app.get_session_var("caller_id"):
            args = ["--caller", app.get_session_var("caller_id")] + args
        transport, protocol = await loop.subprocess_exec(
            lambda: PIOCoreProtocol(exit_future, data_callback),
            get_core_fullpath(),
            *args,
            stdin=None,
            **options.get("spawn", {}),
        )
        await exit_future
        transport.close()
        return {
            "stdout": protocol.stdout,
            "stderr": protocol.stderr,
            "returncode": transport.get_returncode(),
        }

    def _on_exec_data_received(self, exec_options, pipe, data):
        notification_method = exec_options.get(f"{pipe}NotificationMethod")
        if not notification_method:
            return
        aio_create_task(
            self.factory.notify_clients(
                method=notification_method,
                params=[data],
                actor="frontend",
            )
        )
