# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir
from os.path import join
from sys import exit

from click import command, MultiCommand, version_option

from platformio import __version__
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
        mod = __import__("platformio.commands." + name, None, None, ["cli"])
        return mod.cli


@command(cls=PlatformioCLI)
@version_option(__version__)
def cli():
    pass


def main():
    cli()


if __name__ == "__main__":
    exit(main())
