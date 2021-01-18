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

import click
import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

from platformio.commands.home.rpc.handlers.account import AccountRPC
from platformio.commands.home.rpc.handlers.app import AppRPC
from platformio.commands.home.rpc.handlers.ide import IDERPC
from platformio.commands.home.rpc.handlers.misc import MiscRPC
from platformio.commands.home.rpc.handlers.os import OSRPC
from platformio.commands.home.rpc.handlers.piocore import PIOCoreRPC
from platformio.commands.home.rpc.handlers.project import ProjectRPC
from platformio.commands.home.rpc.server import WebSocketJSONRPCServerFactory
from platformio.exception import PlatformioException
from platformio.package.manager.core import get_core_package_dir
from platformio.proc import force_exit


class ShutdownMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and b"__shutdown__" in scope.get("query_string", {}):
            await shutdown_server()
        await self.app(scope, receive, send)


async def shutdown_server(_=None):
    asyncio.get_event_loop().call_later(0.5, force_exit)
    return PlainTextResponse("Server has been shutdown!")


def run_server(host, port, no_open, shutdown_timeout, home_url):
    contrib_dir = get_core_package_dir("contrib-piohome")
    if not os.path.isdir(contrib_dir):
        raise PlatformioException("Invalid path to PIO Home Contrib")

    ws_rpc_factory = WebSocketJSONRPCServerFactory(shutdown_timeout)
    ws_rpc_factory.addHandler(AccountRPC(), namespace="account")
    ws_rpc_factory.addHandler(AppRPC(), namespace="app")
    ws_rpc_factory.addHandler(IDERPC(), namespace="ide")
    ws_rpc_factory.addHandler(MiscRPC(), namespace="misc")
    ws_rpc_factory.addHandler(OSRPC(), namespace="os")
    ws_rpc_factory.addHandler(PIOCoreRPC(), namespace="core")
    ws_rpc_factory.addHandler(ProjectRPC(), namespace="project")

    uvicorn.run(
        Starlette(
            middleware=[Middleware(ShutdownMiddleware)],
            routes=[
                WebSocketRoute("/wsrpc", ws_rpc_factory, name="wsrpc"),
                Route("/__shutdown__", shutdown_server, methods=["POST"]),
                Mount("/", StaticFiles(directory=contrib_dir, html=True)),
            ],
            on_startup=[
                lambda: click.echo(
                    "PIO Home has been started. Press Ctrl+C to shutdown."
                ),
                lambda: None if no_open else click.launch(home_url),
            ],
        ),
        host=host,
        port=port,
        log_level="warning",
    )
