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

# pylint: disable=too-many-locals,too-many-statements

import mimetypes
import os
import socket

import click

from platformio import exception
from platformio.compat import WINDOWS, ensure_python3
from platformio.package.manager.core import get_core_package_dir


@click.command("home", short_help="GUI to manage PlatformIO")
@click.option("--port", type=int, default=8008, help="HTTP port, default=8008")
@click.option(
    "--host",
    default="127.0.0.1",
    help=(
        "HTTP host, default=127.0.0.1. You can open PIO Home for inbound "
        "connections with --host=0.0.0.0"
    ),
)
@click.option("--no-open", is_flag=True)
@click.option(
    "--shutdown-timeout",
    default=0,
    type=int,
    help=(
        "Automatically shutdown server on timeout (in seconds) when no clients "
        "are connected. Default is 0 which means never auto shutdown"
    ),
)
def cli(port, host, no_open, shutdown_timeout):
    # Ensure PIO Home mimetypes are known
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")

    # hook for `platformio-node-helpers`
    if host == "__do_not_start__":
        return

    home_url = "http://%s:%d" % (host, port)
    click.echo(
        "\n".join(
            [
                "",
                "  ___I_",
                " /\\-_--\\   PlatformIO Home",
                "/  \\_-__\\",
                "|[]| [] |  %s" % home_url,
                "|__|____|______________%s" % ("_" * len(host)),
            ]
        )
    )
    click.echo("")
    click.echo("Open PlatformIO Home in your browser by this URL => %s" % home_url)

    if is_port_used(host, port):
        click.secho(
            "PlatformIO Home server is already started in another process.", fg="yellow"
        )
        if not no_open:
            click.launch(home_url)
        return

    run_server(
        host=host,
        port=port,
        no_open=no_open,
        shutdown_timeout=shutdown_timeout,
        home_url=home_url,
    )


def is_port_used(host, port):
    socket.setdefaulttimeout(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if WINDOWS:
        try:
            s.bind((host, port))
            s.close()
            return False
        except (OSError, socket.error):
            pass
    else:
        try:
            s.connect((host, port))
            s.close()
        except socket.error:
            return False

    return True


def run_server(host, port, no_open, shutdown_timeout, home_url):
    # pylint: disable=import-error, import-outside-toplevel

    ensure_python3()

    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Mount, WebSocketRoute
    from starlette.staticfiles import StaticFiles

    from platformio.commands.home.rpc.handlers.account import AccountRPC
    from platformio.commands.home.rpc.handlers.app import AppRPC
    from platformio.commands.home.rpc.handlers.ide import IDERPC
    from platformio.commands.home.rpc.handlers.misc import MiscRPC
    from platformio.commands.home.rpc.handlers.os import OSRPC
    from platformio.commands.home.rpc.handlers.piocore import PIOCoreRPC
    from platformio.commands.home.rpc.handlers.project import ProjectRPC
    from platformio.commands.home.rpc.server import WebSocketJSONRPCServerFactory

    contrib_dir = get_core_package_dir("contrib-piohome")
    if not os.path.isdir(contrib_dir):
        raise exception.PlatformioException("Invalid path to PIO Home Contrib")

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
            routes=[
                WebSocketRoute("/wsrpc", ws_rpc_factory, name="wsrpc"),
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
