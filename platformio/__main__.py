# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir
from os.path import join
from sys import exit as sys_exit
from traceback import format_exc

from click import command, MultiCommand, style, version_option

from platformio import __version__
from platformio.exception import PlatformioException, UnknownCLICommand
from platformio.util import get_source_dir


class PlatformioCLI(MultiCommand):

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
        try:
            mod = __import__("platformio.commands." + name,
                             None, None, ["cli"])
        except ImportError:
            raise UnknownCLICommand(name)
        return mod.cli


@command(cls=PlatformioCLI)
@version_option(__version__, prog_name="PlatformIO")
def cli():
    pass


def main():
    try:
        cli()
    except Exception as e:  # pylint: disable=W0703
        if isinstance(e, PlatformioException):
            sys_exit(style("Error: ", fg="red") + str(e))
        else:
            print format_exc()


if __name__ == "__main__":
    sys_exit(main())
