# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir, makedirs
from os.path import getmtime, isdir, isfile, join
from sys import exit as sys_exit
from time import time
from traceback import format_exc

from click import command, MultiCommand, secho, version_option

from platformio import __version__
from platformio.commands.upgrade import get_latest_version
from platformio.exception import PlatformioException, UnknownCLICommand
from platformio.util import get_home_dir, get_source_dir


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


def autocheck_latest_version():
    check_interval = 3600 * 24 * 7  # 1 week
    checkfile = join(get_home_dir(), ".pioupgrade")
    if isfile(checkfile) and getmtime(checkfile) > (time() - check_interval):
        return False
    if not isdir(get_home_dir()):
        makedirs(get_home_dir())
    with open(checkfile, "w") as f:
        f.write(str(time()))
    return get_latest_version() != __version__


def main():
    try:
        if autocheck_latest_version():
            secho("\nThere is a new version of PlatformIO available.\n"
                  "Please upgrade it via `platformio upgrade` command.\n",
                  fg="yellow")

        cli()
    except Exception as e:  # pylint: disable=W0703
        if isinstance(e, PlatformioException):
            sys_exit("Error: " + str(e))
        else:
            print format_exc()


if __name__ == "__main__":
    sys_exit(main())
