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

import json
import sys

import click
from serial.tools import miniterm

from platformio.exception import MinitermException
from platformio.util import get_serialports


@click.group(short_help="Monitor device or list existing")
def cli():
    pass


@cli.command("list", short_help="List devices")
@click.option("--json-output", is_flag=True)
def device_list(json_output):

    if json_output:
        click.echo(json.dumps(get_serialports()))
        return

    for item in get_serialports():
        click.secho(item['port'], fg="cyan")
        click.echo("-" * len(item['port']))
        click.echo("Hardware ID: %s" % item['hwid'])
        click.echo("Description: %s" % item['description'])
        click.echo("")


@cli.command("monitor", short_help="Monitor device (Serial)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option(
    "--baud", "-b", type=int, default=9600, help="Set baud rate, default=9600")
@click.option(
    "--parity",
    default="N",
    type=click.Choice(["N", "E", "O", "S", "M"]),
    help="Set parity, default=N")
@click.option(
    "--rtscts", is_flag=True, help="Enable RTS/CTS flow control, default=Off")
@click.option(
    "--xonxoff",
    is_flag=True,
    help="Enable software flow control, default=Off")
@click.option(
    "--rts",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial RTS line state")
@click.option(
    "--dtr",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial DTR line state")
@click.option("--echo", is_flag=True, help="Enable local echo, default=Off")
@click.option(
    "--encoding",
    default="UTF-8",
    help="Set the encoding for the serial port (e.g. hexlify, "
    "Latin1, UTF-8), default: UTF-8")
@click.option("--filter", "-f", multiple=True, help="Add text transformation")
@click.option(
    "--eol",
    default="CRLF",
    type=click.Choice(["CR", "LF", "CRLF"]),
    help="End of line mode, default=CRLF")
@click.option(
    "--raw", is_flag=True, help="Do not apply any encodings/transformations")
@click.option(
    "--exit-char",
    type=int,
    default=3,
    help="ASCII code of special character that is used to exit "
    "the application, default=3 (Ctrl+C)")
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
def device_monitor(**kwargs):
    if not kwargs['port']:
        ports = get_serialports(filter_hwid=True)
        if len(ports) == 1:
            kwargs['port'] = ports[0]['port']

    sys.argv = ["monitor"]
    for k, v in kwargs.iteritems():
        if k in ("port", "baud", "rts", "dtr"):
            continue
        k = "--" + k.replace("_", "-")
        if isinstance(v, bool):
            if v:
                sys.argv.append(k)
        elif isinstance(v, tuple):
            for i in v:
                sys.argv.extend([k, i])
        else:
            sys.argv.extend([k, str(v)])

    try:
        miniterm.main(
            default_port=kwargs['port'],
            default_baudrate=kwargs['baud'],
            default_rts=kwargs['rts'],
            default_dtr=kwargs['dtr'])
    except Exception as e:
        raise MinitermException(e)
