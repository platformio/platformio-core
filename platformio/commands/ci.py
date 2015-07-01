# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import stat
from glob import glob
from os import chmod, getenv, makedirs, remove
from os.path import abspath, basename, expanduser, isdir, isfile, join
from shutil import copyfile, copytree, rmtree
from tempfile import mkdtemp

import click

from platformio import app
from platformio.commands.init import cli as cmd_init
from platformio.commands.run import cli as cmd_run
from platformio.exception import CIBuildEnvsEmpty
from platformio.util import get_boards


def validate_path(ctx, param, value):  # pylint: disable=W0613
    invalid_path = None
    value = list(value)
    for i, p in enumerate(value):
        if p.startswith("~"):
            value[i] = expanduser(p)
        value[i] = abspath(value[i])
        if not glob(value[i]):
            invalid_path = p
            break
    try:
        assert invalid_path is None
        return value
    except AssertionError:
        raise click.BadParameter("Found invalid path: %s" % invalid_path)


def validate_boards(ctx, param, value):  # pylint: disable=W0613
    unknown_boards = set(value) - set(get_boards().keys())
    try:
        assert not unknown_boards
        return value
    except AssertionError:
        raise click.BadParameter(
            "%s. Please search for the board types using "
            "`platformio boards` command" % ", ".join(unknown_boards))


@click.command("ci", short_help="Continuous Integration")
@click.argument("src", nargs=-1, callback=validate_path)
@click.option("--lib", "-l", multiple=True, callback=validate_path)
@click.option("--exclude", multiple=True)
@click.option("--board", "-b", multiple=True, callback=validate_boards)
@click.option("--build-dir", default=mkdtemp,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.option("--keep-build-dir", is_flag=True)
@click.option("--project-conf",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              readable=True, resolve_path=True))
@click.option("--verbose", "-v", count=True, default=3)
@click.pass_context
def cli(ctx, src, lib, exclude, board,  # pylint: disable=R0913
        build_dir, keep_build_dir, project_conf, verbose):

    if not src:
        src = getenv("PLATFORMIO_CI_SRC", "").split(":")
    if not src:
        raise click.BadParameter("Missing argument 'src'")

    try:
        app.set_session_var("force_option", True)
        _clean_dir(build_dir)

        for dir_name, patterns in dict(lib=lib, src=src).iteritems():
            if not patterns:
                continue
            contents = []
            for p in patterns:
                contents += glob(p)
            _copy_contents(join(build_dir, dir_name), contents)

        if project_conf and isfile(project_conf):
            copyfile(project_conf, join(build_dir, "platformio.ini"))
        elif not board:
            raise CIBuildEnvsEmpty()

        if exclude:
            _exclude_contents(build_dir, exclude)

        # initialise project
        ctx.invoke(cmd_init, project_dir=build_dir, board=board,
                   disable_auto_uploading=True)

        # process project
        ctx.invoke(cmd_run, project_dir=build_dir, verbose=verbose)
    finally:
        if not keep_build_dir:
            rmtree(
                build_dir, onerror=lambda action, name, exc:
                (chmod(name, stat.S_IWRITE), remove(name))
            )


def _clean_dir(dirpath):
    rmtree(dirpath)
    makedirs(dirpath)


def _copy_contents(dst_dir, contents):
    items = {
        "dirs": set(),
        "files": set()
    }

    for path in contents:
        if isdir(path):
            items['dirs'].add(path)
        elif isfile(path):
            items['files'].add(path)

    dst_dir_name = basename(dst_dir)

    if dst_dir_name == "src" and len(items['dirs']) == 1:
        copytree(list(items['dirs']).pop(), dst_dir)
    else:
        makedirs(dst_dir)
        for d in items['dirs']:
            copytree(d, join(dst_dir, basename(d)))

    if not items['files']:
        return

    if dst_dir_name == "lib":
        dst_dir = join(dst_dir, mkdtemp(dir=dst_dir))

    for f in items['files']:
        copyfile(f, join(dst_dir, basename(f)))


def _exclude_contents(dst_dir, patterns):
    contents = []
    for p in patterns:
        contents += glob(join(dst_dir, p))
    for path in contents:
        path = abspath(path)
        if isdir(path):
            rmtree(path)
        elif isfile(path):
            remove(path)
