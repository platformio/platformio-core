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

# pylint: disable=too-many-locals

import mimetypes
import socket
from os.path import isdir

import click

from platformio import exception
from platformio.compat import WINDOWS
from platformio.managers.core import get_core_package_dir, inject_contrib_pysite


@click.command("home", short_help="PIO Home")
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
    # pylint: disable=import-error, import-outside-toplevel

    # import contrib modules
    inject_contrib_pysite()
    from autobahn.twisted.resource import WebSocketResource
    from twisted.internet import reactor
    from twisted.web import server

    from platformio.commands.home.rpc.handlers.app import AppRPC
    from platformio.commands.home.rpc.handlers.ide import IDERPC
    from platformio.commands.home.rpc.handlers.misc import MiscRPC
    from platformio.commands.home.rpc.handlers.os import OSRPC
    from platformio.commands.home.rpc.handlers.piocore import PIOCoreRPC
    from platformio.commands.home.rpc.handlers.project import ProjectRPC
    from platformio.commands.home.rpc.server import JSONRPCServerFactory
    from platformio.commands.home.web import WebRoot

    factory = JSONRPCServerFactory(shutdown_timeout)
    factory.addHandler(AppRPC(), namespace="app")
    factory.addHandler(IDERPC(), namespace="ide")
    factory.addHandler(MiscRPC(), namespace="misc")
    factory.addHandler(OSRPC(), namespace="os")
    factory.addHandler(PIOCoreRPC(), namespace="core")
    factory.addHandler(ProjectRPC(), namespace="project")

    contrib_dir = get_core_package_dir("contrib-piohome")
    if not isdir(contrib_dir):
        raise exception.PlatformioException("Invalid path to PIO Home Contrib")

    # Ensure PIO Home mimetypes are known
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")

    root = WebRoot(contrib_dir)
    root.putChild(b"wsrpc", WebSocketResource(factory))
    site = server.Site(root)

    # hook for `platformio-node-helpers`
    if host == "__do_not_start__":
        return

    already_started = is_port_used(host, port)
    home_url = "http://%s:%d" % (host, port)
    if not no_open:
        if already_started:
            click.launch(home_url)
        else:
            reactor.callLater(1, lambda: click.launch(home_url))

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

    if already_started:
        click.secho(
            "PlatformIO Home server is already started in another process.", fg="yellow"
        )
        return

    click.echo("PIO Home has been started. Press Ctrl+C to shutdown.")

    reactor.listenTCP(port, site, interface=host)
    reactor.run()


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
