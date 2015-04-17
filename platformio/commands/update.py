# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.commands.lib import lib_update as cmd_lib_update
from platformio.commands.platforms import \
    platforms_update as cmd_platforms_update


@click.command("update",
               short_help="Update installed Platforms, Packages and Libraries")
@click.pass_context
def cli(ctx):
    ctx.invoke(cmd_platforms_update)
    ctx.invoke(cmd_lib_update)
