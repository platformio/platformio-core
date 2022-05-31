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

import click
from ajsonrpc.dispatcher import Dispatcher
from ajsonrpc.manager import AsyncJSONRPCResponseManager
from starlette.endpoints import WebSocketEndpoint

from platformio.compat import aio_create_task, aio_get_running_loop
from platformio.proc import force_exit


class JSONRPCServerFactoryBase:

    connection_nums = 0
    shutdown_timer = None

    def __init__(self, shutdown_timeout=0):
        self.shutdown_timeout = shutdown_timeout
        self.manager = AsyncJSONRPCResponseManager(
            Dispatcher(), is_server_error_verbose=True
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def add_object_handler(self, handler, namespace):
        self.manager.dispatcher.add_object(handler, prefix="%s." % namespace)

    def on_client_connect(self):
        self.connection_nums += 1
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None

    def on_client_disconnect(self):
        self.connection_nums -= 1
        if self.connection_nums < 1:
            self.connection_nums = 0

        if self.connection_nums == 0:
            self.shutdown_by_timeout()

    async def on_shutdown(self):
        pass

    def shutdown_by_timeout(self):
        if self.shutdown_timeout < 1:
            return

        def _auto_shutdown_server():
            click.echo("Automatically shutdown server on timeout")
            force_exit()

        self.shutdown_timer = aio_get_running_loop().call_later(
            self.shutdown_timeout, _auto_shutdown_server
        )


class WebSocketJSONRPCServerFactory(JSONRPCServerFactoryBase):
    def __call__(self, *args, **kwargs):
        ws = WebSocketJSONRPCServer(*args, **kwargs)
        ws.factory = self
        return ws


class WebSocketJSONRPCServer(WebSocketEndpoint):
    encoding = "text"
    factory: WebSocketJSONRPCServerFactory = None

    async def on_connect(self, websocket):
        await websocket.accept()
        self.factory.on_client_connect()  # pylint: disable=no-member

    async def on_receive(self, websocket, data):
        aio_create_task(self._handle_rpc(websocket, data))

    async def on_disconnect(self, websocket, close_code):
        self.factory.on_client_disconnect()  # pylint: disable=no-member

    async def _handle_rpc(self, websocket, data):
        # pylint: disable=no-member
        response = await self.factory.manager.get_response_for_payload(data)
        if response.error and response.error.data:
            click.secho("Error: %s" % response.error.data, fg="red", err=True)
        await websocket.send_text(self.factory.manager.serialize(response.body))
