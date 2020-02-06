# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from glob import glob
from os import getenv, makedirs, remove
from os.path import basename, isdir, isfile, join, realpath
from shutil import copyfile, copytree
from tempfile import mkdtemp

import click

from platformio import app, fs
from platformio.commands.project import project_init as cmd_project_init
from platformio.commands.project import validate_boards
from platformio.commands.run.command import cli as cmd_run
from platformio.compat import glob_escape
from platformio.exception import CIBuildEnvsEmpty
from platformio.project.config import ProjectConfig


def validate_path(ctx, param, value):  # pylint: disable=unused-argument
    invalid_path = None
    value = list(value)
    for i, p in enumerate(value):
        if p.startswith("~"):
            value[i] = fs.expanduser(p)
        value[i] = realpath(value[i])
        if not glob(value[i]):
            invalid_path = p
            break
    try:
        assert invalid_path is None
        return value
    except AssertionError:
        raise click.BadParameter("Found invalid path: %s" % invalid_path)


@click.command("ci", short_help="Continuous Integration")
@click.argument("src", nargs=-1, callback=validate_path)
@click.option("-l", "--lib", multiple=True, callback=validate_path, metavar="DIRECTORY")
@click.option("--exclude", multiple=True)
@click.option("-b", "--board", multiple=True, metavar="ID", callback=validate_boards)
@click.option(
    "--build-dir",
    default=mkdtemp,
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
@click.option("--keep-build-dir", is_flag=True)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
@click.option("-O", "--project-option", multiple=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(  # pylint: disable=too-many-arguments, too-many-branches
    ctx,
    src,
    lib,
    exclude,
    board,
    build_dir,
    keep_build_dir,
    project_conf,
    project_option,
    verbose,
):

    if not src and getenv("PLATFORMIO_CI_SRC"):
        src = validate_path(ctx, None, getenv("PLATFORMIO_CI_SRC").split(":"))
    if not src:
        raise click.BadParameter("Missing argument 'src'")

    try:
        app.set_session_var("force_option", True)

        if not keep_build_dir and isdir(build_dir):
            fs.rmtree(build_dir)
        if not isdir(build_dir):
            makedirs(build_dir)

        for dir_name, patterns in dict(lib=lib, src=src).items():
            if not patterns:
                continue
            contents = []
            for p in patterns:
                contents += glob(p)
            _copy_contents(join(build_dir, dir_name), contents)

        if project_conf and isfile(project_conf):
            _copy_project_conf(build_dir, project_conf)
        elif not board:
            raise CIBuildEnvsEmpty()

        if exclude:
            _exclude_contents(build_dir, exclude)

        # initialise project
        ctx.invoke(
            cmd_project_init,
            project_dir=build_dir,
            board=board,
            project_option=project_option,
        )

        # process project
        ctx.invoke(cmd_run, project_dir=build_dir, verbose=verbose)
    finally:
        if not keep_build_dir:
            fs.rmtree(build_dir)


def _copy_contents(dst_dir, contents):
    items = {"dirs": set(), "files": set()}

    for path in contents:
        if isdir(path):
            items["dirs"].add(path)
        elif isfile(path):
            items["files"].add(path)

    dst_dir_name = basename(dst_dir)

    if dst_dir_name == "src" and len(items["dirs"]) == 1:
        copytree(list(items["dirs"]).pop(), dst_dir, symlinks=True)
    else:
        if not isdir(dst_dir):
            makedirs(dst_dir)
        for d in items["dirs"]:
            copytree(d, join(dst_dir, basename(d)), symlinks=True)

    if not items["files"]:
        return

    if dst_dir_name == "lib":
        dst_dir = join(dst_dir, mkdtemp(dir=dst_dir))

    for f in items["files"]:
        dst_file = join(dst_dir, basename(f))
        if f == dst_file:
            continue
        copyfile(f, dst_file)


def _exclude_contents(dst_dir, patterns):
    contents = []
    for p in patterns:
        contents += glob(join(glob_escape(dst_dir), p))
    for path in contents:
        path = realpath(path)
        if isdir(path):
            fs.rmtree(path)
        elif isfile(path):
            remove(path)


def _copy_project_conf(build_dir, project_conf):
    config = ProjectConfig(project_conf, parse_extra=False)
    if config.has_section("platformio"):
        config.remove_section("platformio")
    config.save(join(build_dir, "platformio.ini"))
