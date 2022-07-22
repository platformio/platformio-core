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

# pylint: disable=line-too-long,too-many-arguments,too-many-locals


import json
import os

import click

from platformio import fs
from platformio.package.commands.install import install_project_dependencies
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.exception import UnknownBoard
from platformio.project.config import ProjectConfig
from platformio.project.helpers import is_platformio_project
from platformio.project.integration.generator import ProjectGenerator


def validate_boards(ctx, param, value):  # pylint: disable=W0613
    pm = PlatformPackageManager()
    for id_ in value:
        try:
            pm.board_config(id_)
        except UnknownBoard as exc:
            raise click.BadParameter(
                "`%s`. Please search for board ID using `platformio boards` "
                "command" % id_
            ) from exc
    return value


@click.command("init", short_help="Initialize a project or update existing")
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
@click.option("-e", "--environment", help="Update existing environment")
@click.option("-O", "--project-option", multiple=True)
@click.option("--env-prefix", default="")
@click.option("--no-install-dependencies", is_flag=True)
@click.option("-s", "--silent", is_flag=True)
def project_init_cmd(
    project_dir,
    board,
    ide,
    environment,
    project_option,
    env_prefix,
    no_install_dependencies,
    silent,
):
    is_new_project = not is_platformio_project(project_dir)
    if is_new_project:
        if not silent:
            print_header(project_dir)
        init_base_project(project_dir)

    if environment:
        update_project_env(project_dir, environment, project_option)
    elif board:
        update_board_envs(project_dir, board, project_option, env_prefix)

    with fs.cd(project_dir):
        generator = None
        config = ProjectConfig.get_instance(os.path.join(project_dir, "platformio.ini"))
        if ide:
            config.validate()
            # init generator and pick the best env if user didn't specify
            generator = ProjectGenerator(config, environment, ide, board)
            if not environment:
                environment = generator.env_name

        # resolve project dependencies
        if not no_install_dependencies and (environment or board):
            install_project_dependencies(
                options=dict(
                    project_dir=project_dir,
                    environments=[environment] if environment else [],
                    silent=silent,
                )
            )

        if generator:
            if not silent:
                click.echo(
                    "Updating metadata for the %s IDE..." % click.style(ide, fg="cyan")
                )
            generator.generate()

    if is_new_project:
        init_cvs_ignore(project_dir)

    if not silent:
        print_footer(is_new_project)


def print_header(project_dir):
    if project_dir == os.getcwd():
        click.secho("\nThe current working directory ", fg="yellow", nl=False)
        try:
            click.secho(project_dir, fg="cyan", nl=False)
        except UnicodeEncodeError:
            click.secho(json.dumps(project_dir), fg="cyan", nl=False)
        click.secho(" will be used for the project.", fg="yellow")
        click.echo("")

    click.echo("The next files/directories have been created in ", nl=False)
    try:
        click.secho(project_dir, fg="cyan")
    except UnicodeEncodeError:
        click.secho(json.dumps(project_dir), fg="cyan")
    click.echo("%s - Put project header files here" % click.style("include", fg="cyan"))
    click.echo(
        "%s - Put here project specific (private) libraries"
        % click.style("lib", fg="cyan")
    )
    click.echo("%s - Put project source files here" % click.style("src", fg="cyan"))
    click.echo(
        "%s - Project Configuration File" % click.style("platformio.ini", fg="cyan")
    )


def print_footer(is_new_project):
    if is_new_project:
        return click.secho(
            "\nProject has been successfully initialized! Useful commands:\n"
            "`pio run` - process/build project from the current directory\n"
            "`pio run --target upload` or `pio run -t upload` "
            "- upload firmware to a target\n"
            "`pio run --target clean` - clean project (remove compiled files)"
            "\n`pio run --help` - additional information",
            fg="green",
        )
    return click.secho(
        "Project has been successfully updated!",
        fg="green",
    )


def init_base_project(project_dir):
    with fs.cd(project_dir):
        config = ProjectConfig()
        config.save()
        dir_to_readme = [
            (config.get("platformio", "src_dir"), None),
            (config.get("platformio", "include_dir"), init_include_readme),
            (config.get("platformio", "lib_dir"), init_lib_readme),
            (config.get("platformio", "test_dir"), init_test_readme),
        ]
        for (path, cb) in dir_to_readme:
            if os.path.isdir(path):
                continue
            os.makedirs(path)
            if cb:
                cb(path)


def init_include_readme(include_dir):
    with open(os.path.join(include_dir, "README"), mode="w", encoding="utf8") as fp:
        fp.write(
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
    with open(os.path.join(lib_dir, "README"), mode="w", encoding="utf8") as fp:
        fp.write(
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
    with open(os.path.join(test_dir, "README"), mode="w", encoding="utf8") as fp:
        fp.write(
            """
This directory is intended for PlatformIO Test Runner and project tests.

Unit Testing is a software testing method by which individual units of
source code, sets of one or more MCU program modules together with associated
control data, usage procedures, and operating procedures, are tested to
determine whether they are fit for use. Unit testing finds problems early
in the development cycle.

More information about PlatformIO Unit Testing:
- https://docs.platformio.org/en/latest/advanced/unit-testing/index.html
""",
        )


def init_cvs_ignore(project_dir):
    conf_path = os.path.join(project_dir, ".gitignore")
    if os.path.isfile(conf_path):
        return
    with open(conf_path, mode="w", encoding="utf8") as fp:
        fp.write(".pio\n")


def update_board_envs(project_dir, board_ids, project_option, env_prefix):
    config = ProjectConfig(
        os.path.join(project_dir, "platformio.ini"), parse_extra=False
    )
    used_boards = []
    for section in config.sections():
        cond = [section.startswith("env:"), config.has_option(section, "board")]
        if all(cond):
            used_boards.append(config.get(section, "board"))

    pm = PlatformPackageManager()
    modified = False
    for id_ in board_ids:
        board_config = pm.board_config(id_)
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

    if modified:
        config.save()


def update_project_env(project_dir, environment, project_option):
    if not project_option:
        return
    config = ProjectConfig(
        os.path.join(project_dir, "platformio.ini"), parse_extra=False
    )

    section = "env:%s" % environment
    if not config.has_section(section):
        config.add_section(section)

    for item in project_option:
        if "=" not in item:
            continue
        _name, _value = item.split("=", 1)
        config.set(section, _name.strip(), _value.strip())

    config.save()
