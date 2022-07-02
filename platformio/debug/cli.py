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
import signal
import subprocess

import click

from platformio import app, exception, fs, proc
from platformio.compat import IS_WINDOWS
from platformio.debug import helpers
from platformio.debug.config.factory import DebugConfigFactory
from platformio.debug.exception import DebugInvalidOptionsError
from platformio.debug.process.gdb import GDBClientProcess
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectEnvsNotAvailableError
from platformio.project.helpers import is_platformio_project
from platformio.project.options import ProjectOptions


@click.command(
    "debug",
    context_settings=dict(ignore_unknown_options=True),
    short_help="Unified Debugger",
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
@click.option("--load-mode", type=ProjectOptions["env.debug_load_mode"].type)
@click.option("--verbose", "-v", is_flag=True)
@click.option("--interface", type=click.Choice(["gdb"]))
@click.argument("__unprocessed", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(
    ctx,
    project_dir,
    project_conf,
    environment,
    load_mode,
    verbose,
    interface,
    __unprocessed,
):
    app.set_session_var("custom_project_conf", project_conf)

    # use env variables from Eclipse or CLion
    for name in ("CWD", "PWD", "PLATFORMIO_PROJECT_DIR"):
        if is_platformio_project(project_dir):
            break
        if os.getenv(name):
            project_dir = os.getenv(name)

    with fs.cd(project_dir):
        return _debug_in_project_dir(
            ctx,
            project_dir,
            project_conf,
            environment,
            load_mode,
            verbose,
            interface,
            __unprocessed,
        )


def _debug_in_project_dir(
    ctx,
    project_dir,
    project_conf,
    environment,
    load_mode,
    verbose,
    interface,
    __unprocessed,
):
    project_config = ProjectConfig.get_instance(project_conf)
    project_config.validate(envs=[environment] if environment else None)
    env_name = environment or helpers.get_default_debug_env(project_config)

    if not interface:
        return helpers.predebug_project(
            ctx, project_dir, project_config, env_name, False, verbose
        )

    env_options = project_config.items(env=env_name, as_dict=True)
    if "platform" not in env_options:
        raise ProjectEnvsNotAvailableError()

    debug_config = DebugConfigFactory.new(
        PlatformFactory.new(env_options["platform"], autoinstall=True),
        project_config,
        env_name,
    )

    if "--version" in __unprocessed:
        return subprocess.run(
            [debug_config.client_executable_path, "--version"], check=True
        )

    try:
        fs.ensure_udev_rules()
    except exception.InvalidUdevRules as exc:
        click.echo(
            helpers.escape_gdbmi_stream("~", str(exc) + "\n")
            if helpers.is_gdbmi_mode()
            else str(exc) + "\n",
            nl=False,
        )

    rebuild_prog = False
    preload = debug_config.load_cmds == ["preload"]
    load_mode = load_mode or debug_config.load_mode
    if load_mode == "always":
        rebuild_prog = preload or not helpers.has_debug_symbols(
            debug_config.program_path
        )
    elif load_mode == "modified":
        rebuild_prog = helpers.is_prog_obsolete(
            debug_config.program_path
        ) or not helpers.has_debug_symbols(debug_config.program_path)

    if not (debug_config.program_path and os.path.isfile(debug_config.program_path)):
        rebuild_prog = True

    if preload or (not rebuild_prog and load_mode != "always"):
        # don't load firmware through debug server
        debug_config.load_cmds = []

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
                helpers.predebug_project(
                    ctx, project_dir, project_config, env_name, preload, verbose
                )
            stream.close()
        else:
            click.echo("Preparing firmware for debugging...")
            helpers.predebug_project(
                ctx, project_dir, project_config, env_name, preload, verbose
            )

        # save SHA sum of newly created prog
        if load_mode == "modified":
            helpers.is_prog_obsolete(debug_config.program_path)

    if not os.path.isfile(debug_config.program_path):
        raise DebugInvalidOptionsError("Program/firmware is missed")

    loop = asyncio.ProactorEventLoop() if IS_WINDOWS else asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    client = GDBClientProcess(project_dir, debug_config)
    coro = client.run(__unprocessed)
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        loop.run_until_complete(coro)
        if IS_WINDOWS:
            client.close()
            # an issue with `asyncio` executor and STIDIN,
            # it cannot be closed gracefully
            proc.force_exit()
    finally:
        client.close()
        loop.close()

    return True
