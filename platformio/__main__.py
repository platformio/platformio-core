# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir
from os.path import join
from sys import exit as sys_exit
from traceback import format_exc

import click

from platformio import __version__, maintenance
from platformio.exception import PlatformioException, UnknownCLICommand
from platformio.util import get_source_dir


class PlatformioCLI(click.MultiCommand):  # pylint: disable=R0904

    def list_commands(self, ctx):
        cmds = []
        for filename in listdir(join(get_source_dir(), "commands")):
            if filename.startswith("__init__"):
                continue
            if filename.endswith(".py"):
                cmds.append(filename[:-3])
        cmds.sort()
        return cmds

    def get_command(self, ctx, name):
        mod = None
        try:
            mod = __import__("platformio.commands." + name,
                             None, None, ["cli"])
        except ImportError:
            raise UnknownCLICommand(name)
        return mod.cli


@click.command(cls=PlatformioCLI)
@click.version_option(__version__, prog_name="PlatformIO")
@click.pass_context
def cli(ctx):
    maintenance.on_platformio_start(ctx)


@cli.resultcallback()
@click.pass_context
def process_result(ctx, result):
    maintenance.on_platformio_end(ctx, result)


def main():
    try:
        cli(None)
    except Exception as e:  # pylint: disable=W0703
        maintenance.on_platformio_exception(e)
        if isinstance(e, PlatformioException):
            click.echo("Error: " + str(e))
            sys_exit(1)
        else:
            print format_exc()


if __name__ == "__main__":
    sys_exit(main())
