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

import glob
import os
import shutil
import tempfile

import click

from platformio import fs
from platformio.exception import CIBuildEnvsEmpty
from platformio.project.commands.init import project_init_cmd, validate_boards
from platformio.project.config import ProjectConfig
from platformio.run.cli import cli as cmd_run


def validate_path(ctx, param, value):  # pylint: disable=unused-argument
    invalid_path = None
    value = list(value)
    for i, p in enumerate(value):
        if p.startswith("~"):
            value[i] = fs.expanduser(p)
        value[i] = os.path.abspath(value[i])
        if not glob.glob(value[i], recursive=True):
            invalid_path = p
            break
    try:
        assert invalid_path is None
        return value
    except AssertionError as exc:
        raise click.BadParameter("Found invalid path: %s" % invalid_path) from exc


@click.command("ci", short_help="Continuous Integration")
@click.argument("src", nargs=-1, callback=validate_path)
@click.option("-l", "--lib", multiple=True, callback=validate_path, metavar="DIRECTORY")
@click.option("--exclude", multiple=True)
@click.option("-b", "--board", multiple=True, metavar="ID", callback=validate_boards)
@click.option(
    "--build-dir",
    default=tempfile.mkdtemp,
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
)
@click.option("--keep-build-dir", is_flag=True)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("-O", "--project-option", multiple=True)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(  # pylint: disable=too-many-arguments,too-many-positional-arguments, too-many-branches
    ctx,
    src,
    lib,
    exclude,
    board,
    build_dir,
    keep_build_dir,
    project_conf,
    project_option,
    environments,
    verbose,
):
    if not src and os.getenv("PLATFORMIO_CI_SRC"):
        src = validate_path(ctx, None, os.getenv("PLATFORMIO_CI_SRC").split(":"))
    if not src:
        raise click.BadParameter("Missing argument 'src'")

    try:
        if not keep_build_dir and os.path.isdir(build_dir):
            fs.rmtree(build_dir)
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        for dir_name, patterns in dict(lib=lib, src=src).items():
            if not patterns:
                continue
            contents = []
            for p in patterns:
                contents += glob.glob(p, recursive=True)
            _copy_contents(os.path.join(build_dir, dir_name), contents)

        if project_conf and os.path.isfile(project_conf):
            _copy_project_conf(build_dir, project_conf)
        elif not board:
            raise CIBuildEnvsEmpty()

        if exclude:
            _exclude_contents(build_dir, exclude)

        # initialise project
        ctx.invoke(
            project_init_cmd,
            project_dir=build_dir,
            boards=board,
            project_options=project_option,
        )

        # process project
        ctx.invoke(
            cmd_run, project_dir=build_dir, environment=environments, verbose=verbose
        )
    finally:
        if not keep_build_dir:
            fs.rmtree(build_dir)


def _copy_contents(dst_dir, contents):  # pylint: disable=too-many-branches
    items = {"dirs": set(), "files": set()}

    for path in contents:
        if os.path.isdir(path):
            items["dirs"].add(path)
        elif os.path.isfile(path):
            items["files"].add(path)

    dst_dir_name = os.path.basename(dst_dir)

    if dst_dir_name == "src" and len(items["dirs"]) == 1:
        if not os.path.isdir(dst_dir):
            shutil.copytree(list(items["dirs"]).pop(), dst_dir, symlinks=True)
    else:
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        for d in items["dirs"]:
            src_dst_dir = os.path.join(dst_dir, os.path.basename(d))
            if not os.path.isdir(src_dst_dir):
                shutil.copytree(d, src_dst_dir, symlinks=True)

    if not items["files"]:
        return

    if dst_dir_name == "lib":
        dst_dir = os.path.join(dst_dir, tempfile.mkdtemp(dir=dst_dir))

    for f in items["files"]:
        dst_file = os.path.join(dst_dir, os.path.basename(f))
        if f == dst_file:
            continue
        shutil.copyfile(f, dst_file)


def _exclude_contents(dst_dir, patterns):
    contents = []
    for p in patterns:
        contents += glob.glob(os.path.join(glob.escape(dst_dir), p), recursive=True)
    for path in contents:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            fs.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


def _copy_project_conf(build_dir, project_conf):
    config = ProjectConfig(project_conf, parse_extra=False)
    if config.has_section("platformio"):
        config.remove_section("platformio")
    config.save(os.path.join(build_dir, "platformio.ini"))
