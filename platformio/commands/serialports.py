# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
import sys

import click
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
@click.option("--rts", default="0", type=click.Choice(["0", "1"]),
              help="Set initial RTS line state, default=0")
@click.option("--dtr", default="0", type=click.Choice(["0", "1"]),
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
              help="ASCII code of special character that is used to exit the "
              "application, default=19 (DEC)")
@click.option("--menu-char", type=int, default=20,
              help="ASCII code of special character that is used to control "
              "miniterm (menu), default=20 (DEC)")
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
