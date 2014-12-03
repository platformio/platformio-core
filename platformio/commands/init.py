# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, makedirs
from os.path import isdir, isfile, join
from shutil import copyfile

import click

from platformio.exception import ProjectInitialized
from platformio.util import get_source_dir


@click.command("init", short_help="Initialize new PlatformIO based project")
@click.option("--project-dir", "-d", default=getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
def cli(project_dir):

    project_file = join(project_dir, "platformio.ini")
    src_dir = join(project_dir, "src")
    lib_dir = join(project_dir, "lib")
    if all([isfile(project_file), isdir(src_dir), isdir(lib_dir)]):
        raise ProjectInitialized()

    if project_dir == getcwd():
        click.secho("The current working directory", fg="yellow", nl=False)
        click.secho(" %s " % project_dir, fg="blue", nl=False)
        click.secho(
            "will be used for the new project.\n"
            "You can specify another project directory via\n"
            "`platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.\n",
            fg="yellow"
        )

    click.echo("The next files/directories will be created in %s" %
               click.style(project_dir, fg="blue"))
    click.echo("%s - Project Configuration File" %
               click.style("platformio.ini", fg="cyan"))
    click.echo("%s - a source directory. Put your source code here" %
               click.style("src", fg="cyan"))
    click.echo("%s - a directory for the project specific libraries" %
               click.style("lib", fg="cyan"))

    if click.confirm("Do you want to continue?"):
        for d in (src_dir, lib_dir):
            if not isdir(d):
                makedirs(d)
        if not isfile(project_file):
            copyfile(join(get_source_dir(), "projectconftpl.ini"),
                     project_file)
        click.secho(
            "Project has been successfully initialized!\n"
            "Now you can process it with `platformio run` command.",
            fg="green"
        )
    else:
        click.secho("Aborted by user", fg="red")
