# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import makedirs
from os.path import isdir, isfile, join
from shutil import copyfile

from click import command, secho

from platformio.exception import ProjectInitialized
from platformio.util import get_source_dir


@command("init", short_help="Initialize new platformio based project")
def cli():

    if isfile("platformio.ini") and isdir("src"):
        raise ProjectInitialized()
    for d in (".pioenvs", "lib", "src"):
        if not isdir(d):
            makedirs(d)
    if not isfile("platformio.ini"):
        copyfile(join(get_source_dir(), "projectconftpl.ini"),
                 "platformio.ini")
    secho("Project successfully initialized.\n"
          "Please put your source code to `src` directory, "
          "external libraries to `lib` and "
          "setup environments in `platformio.ini` file.\n"
          "Then process project with `platformio run` command.",
          fg="green")
