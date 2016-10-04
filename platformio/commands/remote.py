# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import sys
import threading
from os import getcwd
from os.path import isfile, join
from tempfile import mkdtemp
from time import sleep

import click
from serial import VERSION as PYSERIAL_VERSION

from platformio import util
from platformio.commands.device import device_monitor as cmd_device_monitor
from platformio.pioplus import pioplus_call

# pylint: disable=unused-argument


@click.group("remote", short_help="PIO Remote")
@click.option("-a", "--agent", multiple=True)
def cli(**kwargs):
    pass


@cli.group("agent", short_help="Start new agent or list active")
def remote_agent():
    pass


@remote_agent.command("start", short_help="Start agent")
@click.option("-n", "--name")
@click.option("-s", "--share", metavar="E-MAIL")
def remote_agent_start(**kwargs):
    pioplus_call(sys.argv[1:])


@remote_agent.command("list", short_help="List active agents")
def remote_agent_list():
    pioplus_call(sys.argv[1:])


@cli.command("run", short_help="Process project environments")
@click.option("-e", "--environment", multiple=True)
@click.option("-t", "--target", multiple=True)
@click.option("--upload-port")
@click.option(
    "-d",
    "--project-dir",
    default=getcwd,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        writable=True,
        resolve_path=True))
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-r", "--build-remotely", is_flag=True)
def remote_run(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.group("device", short_help="Monitor device or list existing")
def remote_device():
    pass


@remote_device.command("list", short_help="List devices")
@click.option("--json-output", is_flag=True)
def device_list(json_output):
    pioplus_call(sys.argv[1:])


if int(PYSERIAL_VERSION[0]) == 3:

    @remote_device.command("monitor", short_help="Monitor device (Serial)")
    @click.option("--port", "-p", help="Port, a number or a device name")
    @click.option(
        "--baud",
        "-b",
        type=int,
        default=9600,
        help="Set baud rate, default=9600")
    @click.option(
        "--parity",
        default="N",
        type=click.Choice(["N", "E", "O", "S", "M"]),
        help="Set parity, default=N")
    @click.option(
        "--rtscts",
        is_flag=True,
        help="Enable RTS/CTS flow control, default=Off")
    @click.option(
        "--xonxoff",
        is_flag=True,
        help="Enable software flow control, default=Off")
    @click.option(
        "--rts",
        default=None,
        type=click.Choice(["0", "1"]),
        help="Set initial RTS line state")
    @click.option(
        "--dtr",
        default=None,
        type=click.Choice(["0", "1"]),
        help="Set initial DTR line state")
    @click.option(
        "--echo", is_flag=True, help="Enable local echo, default=Off")
    @click.option(
        "--encoding",
        default="UTF-8",
        help="Set the encoding for the serial port (e.g. hexlify, "
        "Latin1, UTF-8), default: UTF-8")
    @click.option(
        "--filter", "-f", multiple=True, help="Add text transformation")
    @click.option(
        "--eol",
        default="CRLF",
        type=click.Choice(["CR", "LF", "CRLF"]),
        help="End of line mode, default=CRLF")
    @click.option(
        "--raw",
        is_flag=True,
        help="Do not apply any encodings/transformations")
    @click.option(
        "--exit-char",
        type=int,
        default=29,
        help="ASCII code of special character that is used to exit "
        "the application, default=29 (DEC)")
    @click.option(
        "--menu-char",
        type=int,
        default=20,
        help="ASCII code of special character that is used to "
        "control miniterm (menu), default=20 (DEC)")
    @click.option(
        "--quiet",
        is_flag=True,
        help="Diagnostics: suppress non-error messages, default=Off")
    @click.pass_context
    def device_monitor(ctx, **kwargs):
        _device_monitor(ctx, **kwargs)
else:

    @remote_device.command("monitor", short_help="Monitor device (Serial)")
    @click.option("--port", "-p", help="Port, a number or a device name")
    @click.option(
        "--baud",
        "-b",
        type=int,
        default=9600,
        help="Set baud rate, default=9600")
    @click.option(
        "--parity",
        default="N",
        type=click.Choice(["N", "E", "O", "S", "M"]),
        help="Set parity, default=N")
    @click.option(
        "--rtscts",
        is_flag=True,
        help="Enable RTS/CTS flow control, default=Off")
    @click.option(
        "--xonxoff",
        is_flag=True,
        help="Enable software flow control, default=Off")
    @click.option(
        "--rts",
        default=None,
        type=click.Choice(["0", "1"]),
        help="Set initial RTS line state, default=0")
    @click.option(
        "--dtr",
        default=None,
        type=click.Choice(["0", "1"]),
        help="Set initial DTR line state, default=0")
    @click.option(
        "--echo", is_flag=True, help="Enable local echo, default=Off")
    @click.option(
        "--cr",
        is_flag=True,
        help="Do not send CR+LF, send CR only, default=Off")
    @click.option(
        "--lf",
        is_flag=True,
        help="Do not send CR+LF, send LF only, default=Off")
    @click.option(
        "--debug",
        "-d",
        count=True,
        help="""Debug received data (escape non-printable chars)
    # --debug can be given multiple times:
    # 0: just print what is received
    # 1: escape non-printable characters, do newlines as unusual
    # 2: escape non-printable characters, newlines too
    # 3: hex dump everything""")
    @click.option(
        "--exit-char",
        type=int,
        default=29,
        help="ASCII code of special character that is used to exit "
        "the application, default=29 (DEC)")
    @click.option(
        "--menu-char",
        type=int,
        default=20,
        help="ASCII code of special character that is used to "
        "control miniterm (menu), default=20 (DEC)")
    @click.option(
        "--quiet",
        is_flag=True,
        help="Diagnostics: suppress non-error messages, default=Off")
    @click.pass_context
    def device_monitor(ctx, **kwargs):
        _device_monitor(ctx, **kwargs)


def _device_monitor(ctx, **kwargs):
    sock_dir = mkdtemp(suffix="pioplus")
    sock_file = join(sock_dir, "sock")
    try:
        t = threading.Thread(
            target=pioplus_call, args=(sys.argv[1:] + ["--sock", sock_dir], ))
        t.start()
        while t.is_alive() and not isfile(sock_file):
            sleep(0.1)
        if not t.is_alive():
            return
        ctx.invoke(cmd_device_monitor, port=open(sock_file).read())
        t.join(2)
    finally:
        util.rmtree_(sock_dir)
