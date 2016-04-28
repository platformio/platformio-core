# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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
from serial import VERSION as PYSERIAL_VERSION
from serial.tools import miniterm

from platformio import app
from platformio.exception import MinitermException
from platformio.util import get_serialports


@click.group(short_help="List or Monitor Serial ports")
def cli():
    pass


@cli.command("list", short_help="List Serial ports")
@click.option("--json-output", is_flag=True)
def serialports_list(json_output):

    if json_output:
        click.echo(json.dumps(get_serialports()))
        return

    for item in get_serialports():
        click.secho(item['port'], fg="cyan")
        click.echo("-" * len(item['port']))
        click.echo("Hardware ID: %s" % item['hwid'])
        click.echo("Description: %s" % item['description'])
        click.echo("")


if int(PYSERIAL_VERSION[0]) == 3:
    @cli.command("monitor", short_help="Monitor Serial port")
    @click.option("--port", "-p", help="Port, a number or a device name")
    @click.option("--baud", "-b", type=int, default=9600,
                  help="Set baud rate, default=9600")
    @click.option("--parity", default="N",
                  type=click.Choice(["N", "E", "O", "S", "M"]),
                  help="Set parity, default=N")
    @click.option("--rtscts", is_flag=True,
                  help="Enable RTS/CTS flow control, default=Off")
    @click.option("--xonxoff", is_flag=True,
                  help="Enable software flow control, default=Off")
    @click.option("--rts", default=None, type=click.Choice(["0", "1"]),
                  help="Set initial RTS line state")
    @click.option("--dtr", default=None, type=click.Choice(["0", "1"]),
                  help="Set initial DTR line state")
    @click.option("--encoding", default="UTF-8",
                  help="Set the encoding for the serial port (e.g. hexlify, "
                  "Latin1, UTF-8), default: UTF-8")
    @click.option("--filter", "-f", multiple=True,
                  help="Add text transformation")
    @click.option("--eol", default="CRLF",
                  type=click.Choice(["CR", "LF", "CRLF"]),
                  help="End of line mode, default=CRLF")
    @click.option("--raw", is_flag=True,
                  help="Do not apply any encodings/transformations")
    @click.option("--exit-char", type=int, default=29,
                  help="ASCII code of special character that is used to exit "
                  "the application, default=29 (DEC)")
    @click.option("--menu-char", type=int, default=20,
                  help="ASCII code of special character that is used to "
                  "control miniterm (menu), default=20 (DEC)")
    @click.option("--quiet", is_flag=True,
                  help="Diagnostics: suppress non-error messages, default=Off")
    def serialports_monitor(**kwargs):
        if not kwargs['port']:
            for item in get_serialports():
                if "VID:PID" in item['hwid']:
                    kwargs['port'] = item['port']
                    break

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
            miniterm.main(  # pylint: disable=E1123
                default_port=kwargs['port'],
                default_baudrate=kwargs['baud'],
                default_rts=kwargs['rts'],
                default_dtr=kwargs['dtr']
            )
        except Exception as e:  # pylint: disable=W0702
            raise MinitermException(e)
else:
    @cli.command("monitor", short_help="Monitor Serial port")
    @click.option("--port", "-p", help="Port, a number or a device name")
    @click.option("--baud", "-b", type=int, default=9600,
                  help="Set baud rate, default=9600")
    @click.option("--parity", default="N",
                  type=click.Choice(["N", "E", "O", "S", "M"]),
                  help="Set parity, default=N")
    @click.option("--rtscts", is_flag=True,
                  help="Enable RTS/CTS flow control, default=Off")
    @click.option("--xonxoff", is_flag=True,
                  help="Enable software flow control, default=Off")
    @click.option("--rts", default=None, type=click.Choice(["0", "1"]),
                  help="Set initial RTS line state, default=0")
    @click.option("--dtr", default=None, type=click.Choice(["0", "1"]),
                  help="Set initial DTR line state, default=0")
    @click.option("--echo", is_flag=True,
                  help="Enable local echo, default=Off")
    @click.option("--cr", is_flag=True,
                  help="Do not send CR+LF, send CR only, default=Off")
    @click.option("--lf", is_flag=True,
                  help="Do not send CR+LF, send LF only, default=Off")
    @click.option("--debug", "-d", count=True,
                  help="""Debug received data (escape non-printable chars)
    # --debug can be given multiple times:
    # 0: just print what is received
    # 1: escape non-printable characters, do newlines as unusual
    # 2: escape non-printable characters, newlines too
    # 3: hex dump everything""")
    @click.option("--exit-char", type=int, default=29,
                  help="ASCII code of special character that is used to exit "
                  "the application, default=29 (DEC)")
    @click.option("--menu-char", type=int, default=20,
                  help="ASCII code of special character that is used to "
                  "control miniterm (menu), default=20 (DEC)")
    @click.option("--quiet", is_flag=True,
                  help="Diagnostics: suppress non-error messages, default=Off")
    def serialports_monitor(**kwargs):
        sys.argv = app.get_session_var("command_ctx").args[1:]

        if not kwargs['port']:
            for item in get_serialports():
                if "VID:PID" in item['hwid']:
                    sys.argv += ["--port", item['port']]
                    break

        try:
            miniterm.main()
        except Exception as e:  # pylint: disable=W0702
            raise MinitermException(e)
