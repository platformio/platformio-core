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

from urllib.parse import parse_qs

import ajsonrpc.utils
import click
from ajsonrpc.core import JSONRPC20Error, JSONRPC20Request
from ajsonrpc.dispatcher import Dispatcher
from ajsonrpc.manager import AsyncJSONRPCResponseManager, JSONRPC20Response
from starlette.endpoints import WebSocketEndpoint

from platformio.compat import aio_create_task, aio_get_running_loop
from platformio.http import InternetConnectionError
from platformio.proc import force_exit

# Remove this line when PR is merged
# https://github.com/pavlov99/ajsonrpc/pull/22
ajsonrpc.utils.is_invalid_params = lambda: False


class JSONRPCServerFactoryBase:
    connection_nums = 0
    shutdown_timer = None

    def __init__(self, shutdown_timeout=0):
        self.shutdown_timeout = shutdown_timeout
        self.manager = AsyncJSONRPCResponseManager(
            Dispatcher(), is_server_error_verbose=True
        )
        self._clients = {}

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def add_object_handler(self, handler, namespace):
        handler.factory = self
        self.manager.dispatcher.add_object(handler, prefix="%s." % namespace)

    def on_client_connect(self, connection, actor=None):
        self._clients[connection] = {"actor": actor}
        self.connection_nums += 1
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None

    def on_client_disconnect(self, connection):
        if connection in self._clients:
            del self._clients[connection]
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

    async def notify_clients(self, method, params=None, actor=None):
        for client, options in self._clients.items():
            if actor and options["actor"] != actor:
                continue
            request = JSONRPC20Request(method, params, is_notification=True)
            await client.send_text(self.manager.serialize(request.body))
        return True


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
        qs = parse_qs(self.scope.get("query_string", b""))
        actors = qs.get(b"actor")
        self.factory.on_client_connect(  # pylint: disable=no-member
            websocket, actor=actors[0].decode() if actors else None
        )

    async def on_receive(self, websocket, data):
        aio_create_task(self._handle_rpc(websocket, data))

    async def on_disconnect(self, websocket, close_code):
        self.factory.on_client_disconnect(websocket)  # pylint: disable=no-member

    async def _handle_rpc(self, websocket, data):
        # pylint: disable=no-member
        response = await self.factory.manager.get_response_for_payload(data)
        if response.error and response.error.data:
            click.secho("Error: %s" % response.error.data, fg="red", err=True)
            if InternetConnectionError.MESSAGE in response.error.data:
                response = JSONRPC20Response(
                    id=response.id,
                    error=JSONRPC20Error(
                        code=4008,
                        message="No Internet Connection",
                        data=response.error.data,
                    ),
                )
        await websocket.send_text(self.factory.manager.serialize(response.body))
