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

# pylint: disable=too-many-arguments, too-many-locals
# pylint: disable=too-many-branches, too-many-statements

import asyncio
import os

import click

from platformio import app, exception, fs, proc
from platformio.commands.platform import platform_install as cmd_platform_install
from platformio.compat import WINDOWS
from platformio.debug import helpers
from platformio.debug.exception import DebugInvalidOptionsError
from platformio.debug.process.client import DebugClientProcess
from platformio.platform.exception import UnknownPlatform
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectEnvsNotAvailableError
from platformio.project.helpers import is_platformio_project, load_project_ide_data


@click.command(
    "debug",
    context_settings=dict(ignore_unknown_options=True),
    short_help="Unified debugger",
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
@click.option("--environment", "-e", metavar="<environment>")
@click.option("--verbose", "-v", is_flag=True)
@click.option("--interface", type=click.Choice(["gdb"]))
@click.argument("__unprocessed", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(ctx, project_dir, project_conf, environment, verbose, interface, __unprocessed):
    app.set_session_var("custom_project_conf", project_conf)

    # use env variables from Eclipse or CLion
    for sysenv in ("CWD", "PWD", "PLATFORMIO_PROJECT_DIR"):
        if is_platformio_project(project_dir):
            break
        if os.getenv(sysenv):
            project_dir = os.getenv(sysenv)

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(project_conf)
        config.validate(envs=[environment] if environment else None)

        env_name = environment or helpers.get_default_debug_env(config)
        env_options = config.items(env=env_name, as_dict=True)
        if not set(env_options.keys()) >= set(["platform", "board"]):
            raise ProjectEnvsNotAvailableError()

        try:
            platform = PlatformFactory.new(env_options["platform"])
        except UnknownPlatform:
            ctx.invoke(
                cmd_platform_install,
                platforms=[env_options["platform"]],
                skip_default_package=True,
            )
            platform = PlatformFactory.new(env_options["platform"])

        debug_options = helpers.configure_initial_debug_options(platform, env_options)
        assert debug_options

    if not interface:
        return helpers.predebug_project(ctx, project_dir, env_name, False, verbose)

    ide_data = load_project_ide_data(project_dir, env_name)
    if not ide_data:
        raise DebugInvalidOptionsError("Could not load a build configuration")

    if "--version" in __unprocessed:
        result = proc.exec_command([ide_data["gdb_path"], "--version"])
        if result["returncode"] == 0:
            return click.echo(result["out"])
        raise exception.PlatformioException("\n".join([result["out"], result["err"]]))

    try:
        fs.ensure_udev_rules()
    except exception.InvalidUdevRules as e:
        click.echo(
            helpers.escape_gdbmi_stream("~", str(e) + "\n")
            if helpers.is_gdbmi_mode()
            else str(e) + "\n",
            nl=False,
        )

    try:
        debug_options = platform.configure_debug_options(debug_options, ide_data)
    except NotImplementedError:
        # legacy for ESP32 dev-platform <=2.0.0
        debug_options["load_cmds"] = helpers.configure_esp32_load_cmds(
            debug_options, ide_data
        )

    rebuild_prog = False
    preload = debug_options["load_cmds"] == ["preload"]
    load_mode = debug_options["load_mode"]
    if load_mode == "always":
        rebuild_prog = preload or not helpers.has_debug_symbols(ide_data["prog_path"])
    elif load_mode == "modified":
        rebuild_prog = helpers.is_prog_obsolete(
            ide_data["prog_path"]
        ) or not helpers.has_debug_symbols(ide_data["prog_path"])
    else:
        rebuild_prog = not os.path.isfile(ide_data["prog_path"])

    if preload or (not rebuild_prog and load_mode != "always"):
        # don't load firmware through debug server
        debug_options["load_cmds"] = []

    if rebuild_prog:
        if helpers.is_gdbmi_mode():
            click.echo(
                helpers.escape_gdbmi_stream(
                    "~", "Preparing firmware for debugging...\n"
                ),
                nl=False,
            )
            stream = helpers.GDBMIConsoleStream()
            with proc.capture_std_streams(stream):
                helpers.predebug_project(ctx, project_dir, env_name, preload, verbose)
            stream.close()
        else:
            click.echo("Preparing firmware for debugging...")
            helpers.predebug_project(ctx, project_dir, env_name, preload, verbose)

        # save SHA sum of newly created prog
        if load_mode == "modified":
            helpers.is_prog_obsolete(ide_data["prog_path"])

    if not os.path.isfile(ide_data["prog_path"]):
        raise DebugInvalidOptionsError("Program/firmware is missed")

    loop = asyncio.ProactorEventLoop() if WINDOWS else asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    client = DebugClientProcess(project_dir, __unprocessed, debug_options, env_options)
    coro = client.run(ide_data["gdb_path"], ide_data["prog_path"])
    loop.run_until_complete(coro)
    if WINDOWS:
        # an issue with asyncio executor and STIDIN, it cannot be closed gracefully
        proc.force_exit()
    loop.close()

    return True
