# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, makedirs
from os.path import isdir, isfile, join
from shutil import copyfile

import click

from platformio import app, exception
from platformio.util import get_boards, get_source_dir


@click.command("init", short_help="Initialize new PlatformIO based project")
@click.option("--project-dir", "-d", default=getcwd,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.option("--board", "-b", multiple=True, metavar="TYPE")
@click.option("--disable-auto-uploading", is_flag=True)
def cli(project_dir, board, disable_auto_uploading):

    project_file = join(project_dir, "platformio.ini")
    src_dir = join(project_dir, "src")
    lib_dir = join(project_dir, "lib")
    if all([isfile(project_file), isdir(src_dir), isdir(lib_dir)]):
        raise exception.ProjectInitialized()

    builtin_boards = set(get_boards().keys())
    if board and not set(board).issubset(builtin_boards):
        raise exception.UnknownBoard(
            ", ".join(set(board).difference(builtin_boards)))

    # ask about auto-uploading
    if board and app.get_setting("enable_prompts"):
        disable_auto_uploading = not click.confirm(
            "\nWould you like to enable firmware auto-uploading when project "
            "is successfully built using `platformio run` command? \n"
            "Don't forget that you can upload firmware manually using "
            "`platformio run --target upload` command."
        )

    if project_dir == getcwd():
        click.secho("\nThe current working directory", fg="yellow", nl=False)
        click.secho(" %s " % project_dir, fg="cyan", nl=False)
        click.secho(
            "will be used for the new project.\n"
            "You can specify another project directory via\n"
            "`platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.\n",
            fg="yellow"
        )

    click.echo("The next files/directories will be created in %s" %
               click.style(project_dir, fg="cyan"))
    click.echo("%s - Project Configuration File. |-> PLEASE EDIT ME <-|" %
               click.style("platformio.ini", fg="cyan"))
    click.echo("%s - Put your source code here" %
               click.style("src", fg="cyan"))
    click.echo("%s - Put here project specific or 3-rd party libraries" %
               click.style("lib", fg="cyan"))

    if (not app.get_setting("enable_prompts") or
            click.confirm("Do you want to continue?")):

        for d in (src_dir, lib_dir):
            if not isdir(d):
                makedirs(d)
        if not isfile(project_file):
            copyfile(join(get_source_dir(), "projectconftpl.ini"),
                     project_file)
            if board:
                fill_project_envs(project_file, board, disable_auto_uploading)
        click.secho(
            "Project has been successfully initialized!\nUseful commands:\n"
            "`platformio run` - process/build project from the current "
            "directory\n"
            "`platformio run --target upload` or `platformio run -t upload` "
            "- upload firmware to embedded board\n"
            "`platformio run --target clean` - clean project (remove compiled "
            "files)",
            fg="green"
        )
    else:
        raise exception.AbortedByUser()


def fill_project_envs(project_file, board_types, disable_auto_uploading):
    builtin_boards = get_boards()
    content = []
    for type_ in board_types:
        if type_ not in builtin_boards:
            continue
        else:
            content.append("")

        data = builtin_boards[type_]
        # find default framework for board
        frameworks = data.get("frameworks")
        content.append("[env:autogen_%s]" % type_)
        content.append("platform = %s" % data['platform'])
        if frameworks:
            content.append("framework = %s" % frameworks[0])
        content.append("board = %s" % type_)

        content.append("%stargets = upload" % ("# " if disable_auto_uploading
                                               else ""))

    with open(project_file, "a") as f:
        f.write("\n".join(content))
