# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import sys

from click import Choice, echo, group, option, secho
from serial.tools import miniterm

from platformio.util import get_serialports


@group(short_help="List or Monitor Serial ports")
def cli():
    pass


@cli.command("list", short_help="List Serial ports")
def serialports_list():

    for item in get_serialports():
        secho(item['port'], fg="cyan")
        echo("----------")
        echo("Hardware ID: %s" % item['hwid'])
        echo("Description: %s" % item['description'])
        echo("")


@cli.command("monitor", short_help="Monitor Serial port")
@option("--port", "-p", help="Port, a number or a device name")
@option("--baud", "-b", type=int, default=9600,
        help="Set baud rate, default=9600")
@option("--parity", default="N", type=Choice(["N", "E", "O", "S", "M"]),
        help="Set parity, default=N")
@option("--rtscts", is_flag=True,
        help="Enable RTS/CTS flow control, default=Off")
@option("--xonxoff", is_flag=True,
        help="Enable software flow control, default=Off")
@option("--rts", default="0", type=Choice(["0", "1"]),
        help="Set initial RTS line state, default=0")
@option("--dtr", default="0", type=Choice(["0", "1"]),
        help="Set initial DTR line state, default=0")
@option("--echo", is_flag=True,
        help="Enable local echo, default=Off")
@option("--cr", is_flag=True,
        help="Do not send CR+LF, send CR only, default=Off")
@option("--lf", is_flag=True,
        help="Do not send CR+LF, send LF only, default=Off")
@option("--debug", "-d", count=True,
        help="""Debug received data (escape non-printable chars)
# --debug can be given multiple times:
# 0: just print what is received
# 1: escape non-printable characters, do newlines as unusual
# 2: escape non-printable characters, newlines too
# 3: hex dump everything""")
@option("--exit-char", type=int, default=0x1d,
        help="ASCII code of special character that is used to exit the "
        "application, default=0x1d")
@option("--menu-char", type=int, default=0x14,
        help="ASCII code of special character that is used to control "
        "miniterm (menu), default=0x14")
@option("--quiet", is_flag=True,
        help="Diagnostics: suppress non-error messages, default=Off")
def serialports_monitor(**_):
    sys.argv = sys.argv[3:]
    try:
        miniterm.main()
    except:  # pylint: disable=W0702
        pass
