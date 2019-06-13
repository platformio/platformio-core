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

from os import makedirs
from os.path import getmtime, isdir, isfile, join
from time import time

import click

from platformio import util
from platformio.project.helpers import (calculate_project_hash,
                                        get_project_dir,
                                        get_project_libdeps_dir)


def handle_legacy_libdeps(project_dir, config):
    legacy_libdeps_dir = join(project_dir, ".piolibdeps")
    if (not isdir(legacy_libdeps_dir)
            or legacy_libdeps_dir == get_project_libdeps_dir()):
        return
    if not config.has_section("env"):
        config.add_section("env")
    lib_extra_dirs = config.get("env", "lib_extra_dirs", [])
    lib_extra_dirs.append(legacy_libdeps_dir)
    config.set("env", "lib_extra_dirs", lib_extra_dirs)
    click.secho(
        "DEPRECATED! A legacy library storage `{0}` has been found in a "
        "project. \nPlease declare project dependencies in `platformio.ini`"
        " file using `lib_deps` option and remove `{0}` folder."
        "\nMore details -> http://docs.platformio.org/page/projectconf/"
        "section_env_library.html#lib-deps".format(legacy_libdeps_dir),
        fg="yellow")


def clean_build_dir(build_dir):
    # remove legacy ".pioenvs" folder
    legacy_build_dir = join(get_project_dir(), ".pioenvs")
    if isdir(legacy_build_dir) and legacy_build_dir != build_dir:
        util.rmtree_(legacy_build_dir)

    structhash_file = join(build_dir, "structure.hash")
    proj_hash = calculate_project_hash()

    # if project's config is modified
    if (isdir(build_dir) and getmtime(join(
            get_project_dir(), "platformio.ini")) > getmtime(build_dir)):
        util.rmtree_(build_dir)

    # check project structure
    if isdir(build_dir) and isfile(structhash_file):
        with open(structhash_file) as f:
            if f.read() == proj_hash:
                return
        util.rmtree_(build_dir)

    if not isdir(build_dir):
        makedirs(build_dir)

    with open(structhash_file, "w") as f:
        f.write(proj_hash)


def print_header(label, is_error=False, fg=None):
    terminal_width, _ = click.get_terminal_size()
    width = len(click.unstyle(label))
    half_line = "=" * int((terminal_width - width - 2) / 2)
    click.secho("%s %s %s" % (half_line, label, half_line),
                fg=fg,
                err=is_error)


def print_summary(results, start_time):
    print_header("[%s]" % click.style("SUMMARY"))

    succeeded_nums = 0
    failed_nums = 0
    envname_max_len = max(
        [len(click.style(envname, fg="cyan")) for (envname, _) in results])
    for (envname, status) in results:
        if status is False:
            failed_nums += 1
            status_str = click.style("FAILED", fg="red")
        elif status is None:
            status_str = click.style("IGNORED", fg="yellow")
        else:
            succeeded_nums += 1
            status_str = click.style("SUCCESS", fg="green")

        format_str = "Environment {0:<%d}\t[{1}]" % envname_max_len
        click.echo(format_str.format(click.style(envname, fg="cyan"),
                                     status_str),
                   err=status is False)

    print_header("%s%d succeeded in %.2f seconds" %
                 ("%d failed, " % failed_nums if failed_nums else "",
                  succeeded_nums, time() - start_time),
                 is_error=failed_nums,
                 fg="red" if failed_nums else "green")
