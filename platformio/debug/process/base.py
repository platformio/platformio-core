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
import signal
import subprocess
import sys
import time

from platformio.compat import (
    IS_WINDOWS,
    aio_create_task,
    aio_get_running_loop,
    get_locale_encoding,
)


class DebugSubprocessProtocol(asyncio.SubprocessProtocol):
    def __init__(self, factory):
        self.factory = factory
        self._is_exited = False

    def connection_made(self, transport):
        self.factory.connection_made(transport)

    def pipe_data_received(self, fd, data):
        pipe_to_cb = [
            self.factory.stdin_data_received,
            self.factory.stdout_data_received,
            self.factory.stderr_data_received,
        ]
        pipe_to_cb[fd](data)

    def connection_lost(self, exc):
        self.process_exited()

    def process_exited(self):
        if self._is_exited:
            return
        self.factory.process_exited()
        self._is_exited = True


class DebugBaseProcess:

    STDOUT_CHUNK_SIZE = 2048
    LOG_FILE = None

    def __init__(self):
        self.transport = None
        self._is_running = False
        self._last_activity = 0
        self._exit_future = None
        self._stdin_read_task = None
        self._std_encoding = get_locale_encoding()

    async def spawn(self, *args, **kwargs):
        wait_until_exit = False
        if "wait_until_exit" in kwargs:
            wait_until_exit = kwargs["wait_until_exit"]
            del kwargs["wait_until_exit"]
        for pipe in ("stdin", "stdout", "stderr"):
            if pipe not in kwargs:
                kwargs[pipe] = subprocess.PIPE
        loop = aio_get_running_loop()
        await loop.subprocess_exec(
            lambda: DebugSubprocessProtocol(self), *args, **kwargs
        )
        if wait_until_exit:
            self._exit_future = loop.create_future()
            await self._exit_future

    def is_running(self):
        return self._is_running

    def connection_made(self, transport):
        self._is_running = True
        self.transport = transport

    def connect_stdin_pipe(self):
        self._stdin_read_task = aio_create_task(self._read_stdin_pipe())

    async def _read_stdin_pipe(self):
        loop = aio_get_running_loop()
        if IS_WINDOWS:
            while True:
                self.stdin_data_received(
                    await loop.run_in_executor(None, sys.stdin.buffer.readline)
                )
        else:
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            while True:
                self.stdin_data_received(await reader.readline())

    def stdin_data_received(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)

    def stdout_data_received(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)
        while data:
            chunk = data[: self.STDOUT_CHUNK_SIZE]
            print(chunk.decode(self._std_encoding, "replace"), end="", flush=True)
            data = data[self.STDOUT_CHUNK_SIZE :]

    def stderr_data_received(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)
        print(
            data.decode(self._std_encoding, "replace"),
            end="",
            file=sys.stderr,
            flush=True,
        )

    def process_exited(self):
        self._is_running = False
        self._last_activity = time.time()
        # Allow terminating via SIGINT/CTRL+C
        signal.signal(signal.SIGINT, signal.default_int_handler)
        if self._stdin_read_task:
            self._stdin_read_task.cancel()
            self._stdin_read_task = None
        if self._exit_future:
            self._exit_future.set_result(True)
            self._exit_future = None

    def terminate(self):
        if not self.is_running() or not self.transport:
            return
        try:
            self.transport.kill()
            self.transport.close()
        except:  # pylint: disable=bare-except
            pass
