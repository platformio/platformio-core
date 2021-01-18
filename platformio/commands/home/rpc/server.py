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

import inspect
import json

import click
import jsonrpc
from starlette.endpoints import WebSocketEndpoint

from platformio.compat import create_task, get_running_loop, is_bytes
from platformio.proc import force_exit


class JSONRPCServerFactoryBase:

    connection_nums = 0
    shutdown_timer = None

    def __init__(self, shutdown_timeout=0):
        self.shutdown_timeout = shutdown_timeout
        self.dispatcher = jsonrpc.Dispatcher()

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def addHandler(self, handler, namespace):
        self.dispatcher.build_method_map(handler, prefix="%s." % namespace)

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

        self.shutdown_timer = get_running_loop().call_later(
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
        create_task(self._handle_rpc(websocket, data))

    async def on_disconnect(self, websocket, close_code):
        self.factory.on_client_disconnect()  # pylint: disable=no-member

    async def _handle_rpc(self, websocket, data):
        response = jsonrpc.JSONRPCResponseManager.handle(
            data, self.factory.dispatcher  # pylint: disable=no-member
        )
        if response.result and inspect.isawaitable(response.result):
            try:
                response.result = await response.result
                response.data["result"] = response.result
                response.error = None
            except Exception as exc:  # pylint: disable=broad-except
                if not isinstance(exc, jsonrpc.exceptions.JSONRPCDispatchException):
                    exc = jsonrpc.exceptions.JSONRPCDispatchException(
                        code=4999, message=str(exc)
                    )
                response.result = None
                response.error = exc.error._data  # pylint: disable=protected-access
                new_data = response.data.copy()
                new_data["error"] = response.error
                del new_data["result"]
                response.data = new_data

        if response.error:
            click.secho("Error: %s" % response.error, fg="red", err=True)
        if "result" in response.data and is_bytes(response.data["result"]):
            response.data["result"] = response.data["result"].decode("utf-8")

        await websocket.send_text(json.dumps(response.data))
