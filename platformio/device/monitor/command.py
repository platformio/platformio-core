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

import os
import sys

import click

from platformio import exception, fs
from platformio.device.finder import SerialPortFinder
from platformio.device.monitor.filters.base import register_filters
from platformio.device.monitor.terminal import get_available_filters, start_terminal
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.options import ProjectOptions


@click.command("monitor", short_help="Monitor device (Serial/Socket)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option(
    "-b",
    "--baud",
    type=ProjectOptions["env.monitor_speed"].type,
    help="Set baud/speed [default=%d]" % ProjectOptions["env.monitor_speed"].default,
)
@click.option(
    "--parity",
    type=ProjectOptions["env.monitor_parity"].type,
    help="Enable parity checking [default=%s]"
    % ProjectOptions["env.monitor_parity"].default,
)
@click.option("--rtscts", is_flag=True, help="Enable RTS/CTS flow control")
@click.option("--xonxoff", is_flag=True, help="Enable software flow control")
@click.option(
    "--rts",
    type=ProjectOptions["env.monitor_rts"].type,
    help="Set initial RTS line state",
)
@click.option(
    "--dtr",
    type=ProjectOptions["env.monitor_dtr"].type,
    help="Set initial DTR line state",
)
@click.option("--echo", is_flag=True, help="Enable local echo")
@click.option(
    "--encoding",
    help=(
        "Set the encoding for the serial port "
        "(e.g. hexlify, Latin-1, UTF-8) [default=%s]"
        % ProjectOptions["env.monitor_encoding"].default
    ),
)
@click.option(
    "-f",
    "--filter",
    "filters",
    multiple=True,
    help="Apply filters/text transformations",
)
@click.option(
    "--eol",
    type=ProjectOptions["env.monitor_eol"].type,
    help="End of line mode [default=%s]" % ProjectOptions["env.monitor_eol"].default,
)
@click.option("--raw", is_flag=True, help=ProjectOptions["env.monitor_raw"].description)
@click.option(
    "--exit-char",
    type=int,
    default=3,
    show_default=True,
    help="ASCII code of special character that is used to exit "
    "the application [default=3 (Ctrl+C)]",
)
@click.option(
    "--menu-char",
    type=int,
    default=20,
    help="ASCII code of special character that is used to "
    "control terminal (menu) [default=20 (DEC)]",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Diagnostics: suppress non-error messages",
)
@click.option(
    "--no-reconnect",
    is_flag=True,
    help="Disable automatic reconnection if the established connection fails",
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "-e",
    "--environment",
    help="Load configuration from `platformio.ini` and the specified environment",
)
def device_monitor_cmd(**options):
    with fs.cd(options["project_dir"]):
        platform = None
        project_options = {}
        try:
            project_options = get_project_options(options["environment"])
            if "platform" in project_options:
                platform = PlatformFactory.new(project_options["platform"])
        except NotPlatformIOProjectError:
            pass

        options = apply_project_monitor_options(options, project_options)
        register_filters(platform=platform, options=options)
        options["port"] = SerialPortFinder(
            board_config=(
                platform.board_config(project_options.get("board"))
                if platform and project_options.get("board")
                else None
            ),
            upload_protocol=project_options.get("upload_protocol"),
            ensure_ready=True,
        ).find(initial_port=options["port"])

        if options["menu_char"] == options["exit_char"]:
            raise exception.UserSideException(
                "--exit-char can not be the same as --menu-char"
            )

        # check for unknown filters
        if options["filters"]:
            known_filters = set(get_available_filters())
            unknown_filters = set(options["filters"]) - known_filters
            if unknown_filters:
                options["filters"] = list(known_filters & set(options["filters"]))
                click.secho(
                    ("Warning! Skipping unknown filters `%s`. Known filters are `%s`")
                    % (", ".join(unknown_filters), ", ".join(sorted(known_filters))),
                    fg="yellow",
                )

        start_terminal(options)


def get_project_options(environment=None):
    config = ProjectConfig.get_instance()
    config.validate(envs=[environment] if environment else None)
    environment = environment or config.get_default_env()
    return config.items(env=environment, as_dict=True)


def apply_project_monitor_options(initial_options, project_options):
    for option_meta in ProjectOptions.values():
        if option_meta.group != "monitor":
            continue
        cli_key = option_meta.name.split("_", 1)[1]
        if cli_key == "speed":
            cli_key = "baud"
        # value set from CLI, skip overriding
        if initial_options[cli_key] not in (None, (), []) and (
            option_meta.type != click.BOOL or f"--{cli_key}" in sys.argv[1:]
        ):
            continue
        initial_options[cli_key] = project_options.get(
            option_meta.name, option_meta.default
        )
    return initial_options
