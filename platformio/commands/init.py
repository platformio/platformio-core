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

from os import getcwd

import click

from platformio import exception
from platformio.managers.platform import PlatformManager
from platformio.project.generator import ProjectGenerator


def validate_boards(ctx, param, value):  # pylint: disable=unused-argument
    pm = PlatformManager()
    for id_ in value:
        try:
            pm.board_config(id_)
        except exception.UnknownBoard:
            raise click.BadParameter(
                "`%s`. Please search for board ID using `platformio boards` "
                "command" % id_)
    return value


@click.command(
    "init", short_help="Initialize PlatformIO project or update existing")
@click.option(
    "--project-dir",
    "-d",
    default=getcwd,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True))
@click.option(
    "-b", "--board", multiple=True, metavar="ID", callback=validate_boards)
@click.option("-p", "--platform")
@click.option("-f", "--framework")
@click.option("--ide", type=click.Choice(ProjectGenerator.get_supported_ide()))
@click.option("--vcs", type=click.Choice(ProjectGenerator.get_supported_vcs()))
@click.option("--ci", type=click.Choice(ProjectGenerator.get_supported_ci()))
@click.option(
    "-L", "--list-templates", help="List available source code templates")
@click.option("-t", "--template")
@click.option("-T", "--template-var", multiple=True)
@click.option("--env-prefix", default="")
@click.option("-E", "--env-option", multiple=True)
@click.option(
    "-O",
    "--project-option",
    multiple=True,
    help="Deprecated. Use `--env-option` instead")
@click.option("-s", "--silent", is_flag=True)
def cli(  # pylint: disable=too-many-arguments,too-many-locals
        project_dir, board, platform, framework, ide, vcs, ci, list_templates,
        template, template_var, env_prefix, env_option, project_option,
        silent):
    if not silent:
        if project_dir == getcwd():
            click.secho(
                "\nThe current working directory", fg="yellow", nl=False)
            click.secho(" %s " % project_dir, fg="cyan", nl=False)
            click.secho(
                "will be used for project.\n"
                "You can specify another project directory via\n"
                "`platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.",
                fg="yellow")
            click.echo("")

        click.echo("The next files/directories have been created in %s" %
                   click.style(project_dir, fg="cyan"))
        click.echo("%s - Project Configuration File" % click.style(
            "platformio.ini", fg="cyan"))
        click.echo(
            "%s - Put your source files here" % click.style("src", fg="cyan"))
        click.echo("%s - Put here project specific (private) libraries" %
                   click.style("lib", fg="cyan"))

    pg = ProjectGenerator(
        project_dir,
        dict(
            boards=list(board),
            platform=platform,
            framework=framework,
            ide=ide,
            template=template,
            template_vars=list(template_var),
            env_prefix=env_prefix,
            env_options=list(env_option) + list(project_option),
            vcs=vcs,
            ci=ci))

    if ide:
        # install development platform before (show progress)
        pm = PlatformManager()
        for name in pg.project_config.get_env_names():
            platform = pg.project_config.env_get(name, "platform")
            framework = pg.project_config.env_get(name, "framework")
            if not platform:
                continue
            if framework:
                pm.install(
                    platform,
                    with_packages=["framework-%s" % framework],
                    silent=True)
            else:
                pm.install(platform, silent=True)

    pg.generate()

    if not silent:
        click.secho(
            "\nProject has been successfully initialized!\nUseful commands:\n"
            "`platformio run` - process/build project from the current "
            "directory\n"
            "`platformio run --target upload` or `platformio run -t upload` "
            "- upload firmware to embedded board\n"
            "`platformio run --target clean` - clean project (remove compiled "
            "files)\n"
            "`platformio run --help` - additional information",
            fg="green")
