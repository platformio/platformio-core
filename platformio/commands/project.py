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

# pylint: disable=too-many-arguments,too-many-locals, too-many-branches

import os

import click
from tabulate import tabulate

from platformio import exception, fs
from platformio.commands.platform import platform_install as cli_platform_install
from platformio.ide.projectgenerator import ProjectGenerator
from platformio.managers.platform import PlatformManager
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.helpers import is_platformio_project


@click.group(short_help="Project Manager")
def cli():
    pass


@cli.command("config", short_help="Show computed configuration")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option("--json-output", is_flag=True)
def project_config(project_dir, json_output):
    if not is_platformio_project(project_dir):
        raise NotPlatformIOProjectError(project_dir)
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
    if json_output:
        return click.echo(config.to_json())
    click.echo(
        "Computed project configuration for %s" % click.style(project_dir, fg="cyan")
    )
    for section, options in config.as_tuple():
        click.echo()
        click.secho(section, fg="cyan")
        click.echo("-" * len(section))
        click.echo(
            tabulate(
                [
                    (name, "=", "\n".join(value) if isinstance(value, list) else value)
                    for name, value in options
                ],
                tablefmt="plain",
            )
        )
    return None


def validate_boards(ctx, param, value):  # pylint: disable=W0613
    pm = PlatformManager()
    for id_ in value:
        try:
            pm.board_config(id_)
        except exception.UnknownBoard:
            raise click.BadParameter(
                "`%s`. Please search for board ID using `platformio boards` "
                "command" % id_
            )
    return value


@cli.command("init", short_help="Initialize a project or update existing")
@click.option(
    "--project-dir",
    "-d",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option("-b", "--board", multiple=True, metavar="ID", callback=validate_boards)
@click.option("--ide", type=click.Choice(ProjectGenerator.get_supported_ides()))
@click.option("-O", "--project-option", multiple=True)
@click.option("--env-prefix", default="")
@click.option("-s", "--silent", is_flag=True)
@click.pass_context
def project_init(
    ctx,  # pylint: disable=R0913
    project_dir,
    board,
    ide,
    project_option,
    env_prefix,
    silent,
):
    if not silent:
        if project_dir == os.getcwd():
            click.secho("\nThe current working directory", fg="yellow", nl=False)
            click.secho(" %s " % project_dir, fg="cyan", nl=False)
            click.secho("will be used for the project.", fg="yellow")
            click.echo("")

        click.echo(
            "The next files/directories have been created in %s"
            % click.style(project_dir, fg="cyan")
        )
        click.echo(
            "%s - Put project header files here" % click.style("include", fg="cyan")
        )
        click.echo(
            "%s - Put here project specific (private) libraries"
            % click.style("lib", fg="cyan")
        )
        click.echo("%s - Put project source files here" % click.style("src", fg="cyan"))
        click.echo(
            "%s - Project Configuration File" % click.style("platformio.ini", fg="cyan")
        )

    is_new_project = not is_platformio_project(project_dir)
    if is_new_project:
        init_base_project(project_dir)

    if board:
        fill_project_envs(
            ctx, project_dir, board, project_option, env_prefix, ide is not None
        )

    if ide:
        pg = ProjectGenerator(project_dir, ide, board)
        pg.generate()

    if is_new_project:
        init_ci_conf(project_dir)
        init_cvs_ignore(project_dir)

    if silent:
        return

    if ide:
        click.secho(
            "\nProject has been successfully %s including configuration files "
            "for `%s` IDE." % ("initialized" if is_new_project else "updated", ide),
            fg="green",
        )
    else:
        click.secho(
            "\nProject has been successfully %s! Useful commands:\n"
            "`pio run` - process/build project from the current directory\n"
            "`pio run --target upload` or `pio run -t upload` "
            "- upload firmware to a target\n"
            "`pio run --target clean` - clean project (remove compiled files)"
            "\n`pio run --help` - additional information"
            % ("initialized" if is_new_project else "updated"),
            fg="green",
        )


def init_base_project(project_dir):
    with fs.cd(project_dir):
        config = ProjectConfig()
        config.save()
        dir_to_readme = [
            (config.get_optional_dir("src"), None),
            (config.get_optional_dir("include"), init_include_readme),
            (config.get_optional_dir("lib"), init_lib_readme),
            (config.get_optional_dir("test"), init_test_readme),
        ]
        for (path, cb) in dir_to_readme:
            if os.path.isdir(path):
                continue
            os.makedirs(path)
            if cb:
                cb(path)


def init_include_readme(include_dir):
    fs.write_file_contents(
        os.path.join(include_dir, "README"),
        """
This directory is intended for project header files.

A header file is a file containing C declarations and macro definitions
to be shared between several project source files. You request the use of a
header file in your project source file (C, C++, etc) located in `src` folder
by including it, with the C preprocessing directive `#include'.

```src/main.c

#include "header.h"

int main (void)
{
 ...
}
```

Including a header file produces the same results as copying the header file
into each source file that needs it. Such copying would be time-consuming
and error-prone. With a header file, the related declarations appear
in only one place. If they need to be changed, they can be changed in one
place, and programs that include the header file will automatically use the
new version when next recompiled. The header file eliminates the labor of
finding and changing all the copies as well as the risk that a failure to
find one copy will result in inconsistencies within a program.

In C, the usual convention is to give header files names that end with `.h'.
It is most portable to use only letters, digits, dashes, and underscores in
header file names, and at most one dot.

Read more about using header files in official GCC documentation:

* Include Syntax
* Include Operation
* Once-Only Headers
* Computed Includes

https://gcc.gnu.org/onlinedocs/cpp/Header-Files.html
""",
    )


def init_lib_readme(lib_dir):
    # pylint: disable=line-too-long
    fs.write_file_contents(
        os.path.join(lib_dir, "README"),
        """
This directory is intended for project specific (private) libraries.
PlatformIO will compile them to static libraries and link into executable file.

The source code of each library should be placed in a an own separate directory
("lib/your_library_name/[here are source files]").

For example, see a structure of the following two libraries `Foo` and `Bar`:

|--lib
|  |
|  |--Bar
|  |  |--docs
|  |  |--examples
|  |  |--src
|  |     |- Bar.c
|  |     |- Bar.h
|  |  |- library.json (optional, custom build options, etc) https://docs.platformio.org/page/librarymanager/config.html
|  |
|  |--Foo
|  |  |- Foo.c
|  |  |- Foo.h
|  |
|  |- README --> THIS FILE
|
|- platformio.ini
|--src
   |- main.c

and a contents of `src/main.c`:
```
#include <Foo.h>
#include <Bar.h>

int main (void)
{
  ...
}

```

PlatformIO Library Dependency Finder will find automatically dependent
libraries scanning project source files.

More information about PlatformIO Library Dependency Finder
- https://docs.platformio.org/page/librarymanager/ldf.html
""",
    )


def init_test_readme(test_dir):
    fs.write_file_contents(
        os.path.join(test_dir, "README"),
        """
This directory is intended for PIO Unit Testing and project tests.

Unit Testing is a software testing method by which individual units of
source code, sets of one or more MCU program modules together with associated
control data, usage procedures, and operating procedures, are tested to
determine whether they are fit for use. Unit testing finds problems early
in the development cycle.

More information about PIO Unit Testing:
- https://docs.platformio.org/page/plus/unit-testing.html
""",
    )


def init_ci_conf(project_dir):
    conf_path = os.path.join(project_dir, ".travis.yml")
    if os.path.isfile(conf_path):
        return
    fs.write_file_contents(
        conf_path,
        """# Continuous Integration (CI) is the practice, in software
# engineering, of merging all developer working copies with a shared mainline
# several times a day < https://docs.platformio.org/page/ci/index.html >
#
# Documentation:
#
# * Travis CI Embedded Builds with PlatformIO
#   < https://docs.travis-ci.com/user/integration/platformio/ >
#
# * PlatformIO integration with Travis CI
#   < https://docs.platformio.org/page/ci/travis.html >
#
# * User Guide for `platformio ci` command
#   < https://docs.platformio.org/page/userguide/cmd_ci.html >
#
#
# Please choose one of the following templates (proposed below) and uncomment
# it (remove "# " before each line) or use own configuration according to the
# Travis CI documentation (see above).
#


#
# Template #1: General project. Test it using existing `platformio.ini`.
#

# language: python
# python:
#     - "2.7"
#
# sudo: false
# cache:
#     directories:
#         - "~/.platformio"
#
# install:
#     - pip install -U platformio
#     - platformio update
#
# script:
#     - platformio run


#
# Template #2: The project is intended to be used as a library with examples.
#

# language: python
# python:
#     - "2.7"
#
# sudo: false
# cache:
#     directories:
#         - "~/.platformio"
#
# env:
#     - PLATFORMIO_CI_SRC=path/to/test/file.c
#     - PLATFORMIO_CI_SRC=examples/file.ino
#     - PLATFORMIO_CI_SRC=path/to/test/directory
#
# install:
#     - pip install -U platformio
#     - platformio update
#
# script:
#     - platformio ci --lib="." --board=ID_1 --board=ID_2 --board=ID_N
""",
    )


def init_cvs_ignore(project_dir):
    conf_path = os.path.join(project_dir, ".gitignore")
    if os.path.isfile(conf_path):
        return
    fs.write_file_contents(conf_path, ".pio\n")


def fill_project_envs(
    ctx, project_dir, board_ids, project_option, env_prefix, force_download
):
    config = ProjectConfig(
        os.path.join(project_dir, "platformio.ini"), parse_extra=False
    )
    used_boards = []
    for section in config.sections():
        cond = [section.startswith("env:"), config.has_option(section, "board")]
        if all(cond):
            used_boards.append(config.get(section, "board"))

    pm = PlatformManager()
    used_platforms = []
    modified = False
    for id_ in board_ids:
        board_config = pm.board_config(id_)
        used_platforms.append(board_config["platform"])
        if id_ in used_boards:
            continue
        used_boards.append(id_)
        modified = True

        envopts = {"platform": board_config["platform"], "board": id_}
        # find default framework for board
        frameworks = board_config.get("frameworks")
        if frameworks:
            envopts["framework"] = frameworks[0]

        for item in project_option:
            if "=" not in item:
                continue
            _name, _value = item.split("=", 1)
            envopts[_name.strip()] = _value.strip()

        section = "env:%s%s" % (env_prefix, id_)
        config.add_section(section)

        for option, value in envopts.items():
            config.set(section, option, value)

    if force_download and used_platforms:
        _install_dependent_platforms(ctx, used_platforms)

    if modified:
        config.save()


def _install_dependent_platforms(ctx, platforms):
    installed_platforms = [p["name"] for p in PlatformManager().get_installed()]
    if set(platforms) <= set(installed_platforms):
        return
    ctx.invoke(
        cli_platform_install, platforms=list(set(platforms) - set(installed_platforms))
    )
