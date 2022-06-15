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

import click

from platformio import exception, fs
from platformio.device.finder import find_serial_port
from platformio.device.monitor.filters.base import register_filters
from platformio.device.monitor.terminal import start_terminal
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.options import ProjectOptions


@click.command("monitor", short_help="Monitor device (Serial/Socket)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option(
    "-b",
    "--baud",
    type=int,
    show_default=True,
    help="Set baud/speed [default=%d]" % ProjectOptions["env.monitor_speed"].default,
)
@click.option(
    "--parity",
    default="N",
    show_default=True,
    type=click.Choice(["N", "E", "O", "S", "M"]),
    help="Set parity",
)
@click.option("--rtscts", is_flag=True, help="Enable RTS/CTS flow control")
@click.option("--xonxoff", is_flag=True, help="Enable software flow control")
@click.option(
    "--rts", default=None, type=click.IntRange(0, 1), help="Set initial RTS line state"
)
@click.option(
    "--dtr", default=None, type=click.IntRange(0, 1), help="Set initial DTR line state"
)
@click.option("--echo", is_flag=True, help="Enable local echo")
@click.option(
    "--encoding",
    default="UTF-8",
    show_default=True,
    help="Set the encoding for the serial port (e.g. hexlify, Latin1, UTF-8)",
)
@click.option(
    "-f", "--filter", "filters", multiple=True, help="Add filters/text transformations"
)
@click.option(
    "--eol",
    default="CRLF",
    show_default=True,
    type=click.Choice(["CR", "LF", "CRLF"]),
    help="End of line mode",
)
@click.option("--raw", is_flag=True, help="Do not apply any encodings/transformations")
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
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "-e",
    "--environment",
    help="Load configuration from `platformio.ini` and the specified environment",
)
def device_monitor_cmd(**options):
    platform = None
    project_options = {}
    with fs.cd(options["project_dir"]):
        try:
            project_options = get_project_options(options["environment"])
            options = apply_project_monitor_options(options, project_options)
            if "platform" in project_options:
                platform = PlatformFactory.new(project_options["platform"])
        except NotPlatformIOProjectError:
            pass
        register_filters(platform=platform, options=options)
        options["port"] = find_serial_port(
            initial_port=options["port"],
            board_config=platform.board_config(project_options.get("board"))
            if platform and project_options.get("board")
            else None,
            upload_protocol=project_options.get("upload_protocol"),
            ensure_ready=True,
        )

    options["baud"] = options["baud"] or ProjectOptions["env.monitor_speed"].default

    if options["menu_char"] == options["exit_char"]:
        raise exception.UserSideException(
            "--exit-char can not be the same as --menu-char"
        )

    start_terminal(options)


def get_project_options(environment=None):
    config = ProjectConfig.get_instance()
    config.validate(envs=[environment] if environment else None)
    environment = environment or config.get_default_env()
    return config.items(env=environment, as_dict=True)


def apply_project_monitor_options(initial_options, project_options):
    for k in ("port", "speed", "rts", "dtr"):
        k2 = "monitor_%s" % k
        if k == "speed":
            k = "baud"
        if initial_options[k] is None and k2 in project_options:
            initial_options[k] = project_options[k2]
            if k != "port":
                initial_options[k] = int(initial_options[k])
    return initial_options
