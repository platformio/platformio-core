# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir
from os.path import join
from sys import exit as sys_exit
from traceback import format_exc

import click
import requests

from platformio import __version__, exception, maintenance
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
            raise exception.UnknownCLICommand(name)
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
        # https://urllib3.readthedocs.org
        # /en/latest/security.html#insecureplatformwarning
        requests.packages.urllib3.disable_warnings()

        cli(None)
    except Exception as e:  # pylint: disable=W0703
        if not isinstance(e, exception.ReturnErrorCode):
            maintenance.on_platformio_exception(e)
            error_str = "Error: "
            if isinstance(e, exception.PlatformioException):
                error_str += str(e)
            else:
                error_str += format_exc()
            click.secho(error_str, fg="red", err=True)
        sys_exit(1)


if __name__ == "__main__":
    sys_exit(main())
