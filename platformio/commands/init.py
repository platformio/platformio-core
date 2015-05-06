# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, makedirs
from os.path import isdir, isfile, join
from shutil import copyfile

import click

from platformio import app, exception
from platformio.ide.projectgenerator import ProjectGenerator
from platformio.util import get_boards, get_source_dir


def validate_boards(ctx, param, value):  # pylint: disable=W0613
    unknown_boards = set(value) - set(get_boards().keys())
    try:
        assert not unknown_boards
        return value
    except AssertionError:
        raise click.BadParameter(
            "%s. Please search for the board types using "
            "`platformio boards` command" % ", ".join(unknown_boards))


@click.command("init", short_help="Initialize new PlatformIO based project")
@click.option("--project-dir", "-d", default=getcwd,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.option("--board", "-b", multiple=True, metavar="TYPE",
              callback=validate_boards)
@click.option("--ide",
              type=click.Choice(ProjectGenerator.get_supported_ides()))
@click.option("--disable-auto-uploading", is_flag=True)
@click.option("--env-prefix", default="")
def cli(project_dir, board, ide, disable_auto_uploading, env_prefix):

    # ask about auto-uploading
    if board and app.get_setting("enable_prompts"):
        disable_auto_uploading = not click.confirm(
            "Would you like to enable firmware auto-uploading when project "
            "is successfully built using `platformio run` command? \n"
            "Don't forget that you can upload firmware manually using "
            "`platformio run --target upload` command."
        )
        click.echo("")

    if project_dir == getcwd():
        click.secho("\nThe current working directory", fg="yellow", nl=False)
        click.secho(" %s " % project_dir, fg="cyan", nl=False)
        click.secho(
            "will be used for project.\n"
            "You can specify another project directory via\n"
            "`platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.",
            fg="yellow"
        )
        click.echo("")

    click.echo("The next files/directories will be created in %s" %
               click.style(project_dir, fg="cyan"))
    click.echo("%s - Project Configuration File. |-> PLEASE EDIT ME <-|" %
               click.style("platformio.ini", fg="cyan"))
    click.echo("%s - Put your source code here" %
               click.style("src", fg="cyan"))
    click.echo("%s - Put here project specific or 3-rd party libraries" %
               click.style("lib", fg="cyan"))

    if (app.get_setting("enable_prompts") and
            not click.confirm("Do you want to continue?")):
        raise exception.AbortedByUser()

    project_file = join(project_dir, "platformio.ini")
    src_dir = join(project_dir, "src")
    lib_dir = join(project_dir, "lib")

    for d in (src_dir, lib_dir):
        if not isdir(d):
            makedirs(d)

    if not isfile(project_file):
        copyfile(join(get_source_dir(), "projectconftpl.ini"),
                 project_file)

    if board:
        fill_project_envs(
            project_file, board, disable_auto_uploading, env_prefix)

    if ide:
        pg = ProjectGenerator(project_dir, ide)
        pg.generate()

    click.secho(
        "\nProject has been successfully initialized!\nUseful commands:\n"
        "`platformio run` - process/build project from the current "
        "directory\n"
        "`platformio run --target upload` or `platformio run -t upload` "
        "- upload firmware to embedded board\n"
        "`platformio run --target clean` - clean project (remove compiled "
        "files)",
        fg="green"
    )


def fill_project_envs(project_file, board_types, disable_auto_uploading,
                      env_prefix):
    builtin_boards = get_boards()
    content = []
    used_envs = []

    with open(project_file) as f:
        used_envs = [l.strip() for l in f.read().splitlines() if
                     l.strip().startswith("[env:")]

    for type_ in board_types:
        data = builtin_boards[type_]
        env_name = "[env:%s%s]" % (env_prefix, type_)

        if env_name in used_envs:
            continue

        content.append("")
        content.append(env_name)
        content.append("platform = %s" % data['platform'])

        # find default framework for board
        frameworks = data.get("frameworks")
        if frameworks:
            content.append("framework = %s" % frameworks[0])

        content.append("board = %s" % type_)
        content.append("%stargets = upload" % ("# " if disable_auto_uploading
                                               else ""))

    if not content:
        return

    with open(project_file, "a") as f:
        content.append("")
        f.write("\n".join(content))
