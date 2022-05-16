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
from serial.tools import miniterm

from platformio import exception, fs
from platformio.device.filters.base import register_filters
from platformio.device.finder import find_serial_port
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.options import ProjectOptions


@click.command("monitor", short_help="Monitor device (Serial/Socket)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option(
    "--baud",
    "-b",
    type=int,
    help="Set baud rate, default=%d" % ProjectOptions["env.monitor_speed"].default,
)
@click.option(
    "--parity",
    default="N",
    type=click.Choice(["N", "E", "O", "S", "M"]),
    help="Set parity, default=N",
)
@click.option("--rtscts", is_flag=True, help="Enable RTS/CTS flow control, default=Off")
@click.option(
    "--xonxoff", is_flag=True, help="Enable software flow control, default=Off"
)
@click.option(
    "--rts", default=None, type=click.IntRange(0, 1), help="Set initial RTS line state"
)
@click.option(
    "--dtr", default=None, type=click.IntRange(0, 1), help="Set initial DTR line state"
)
@click.option("--echo", is_flag=True, help="Enable local echo, default=Off")
@click.option(
    "--encoding",
    default="UTF-8",
    help="Set the encoding for the serial port (e.g. hexlify, "
    "Latin1, UTF-8), default: UTF-8",
)
@click.option("--filter", "-f", multiple=True, help="Add filters/text transformations")
@click.option(
    "--eol",
    default="CRLF",
    type=click.Choice(["CR", "LF", "CRLF"]),
    help="End of line mode, default=CRLF",
)
@click.option("--raw", is_flag=True, help="Do not apply any encodings/transformations")
@click.option(
    "--exit-char",
    type=int,
    default=3,
    help="ASCII code of special character that is used to exit "
    "the application, default=3 (Ctrl+C)",
)
@click.option(
    "--menu-char",
    type=int,
    default=20,
    help="ASCII code of special character that is used to "
    "control miniterm (menu), default=20 (DEC)",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Diagnostics: suppress non-error messages, default=Off",
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
    help="Load configuration from `platformio.ini` and specified environment",
)
def device_monitor_cmd(**kwargs):  # pylint: disable=too-many-branches
    project_options = {}
    platform = None
    with fs.cd(kwargs["project_dir"]):
        try:
            project_options = get_project_options(kwargs["environment"])
            kwargs = apply_project_monitor_options(kwargs, project_options)
            if "platform" in project_options:
                platform = PlatformFactory.new(project_options["platform"])
        except NotPlatformIOProjectError:
            pass
        register_filters(platform=platform, options=kwargs)
        kwargs["port"] = find_serial_port(
            initial_port=kwargs["port"],
            board_config=platform.board_config(project_options.get("board"))
            if platform and project_options.get("board")
            else None,
            upload_protocol=project_options.get("upload_port"),
        )

    # override system argv with patched options
    sys.argv = ["monitor"] + project_options_to_monitor_argv(
        kwargs,
        project_options,
        ignore=("port", "baud", "rts", "dtr", "environment", "project_dir"),
    )

    if not kwargs["quiet"]:
        click.echo(
            "--- Available filters and text transformations: %s"
            % ", ".join(sorted(miniterm.TRANSFORMATIONS.keys()))
        )
        click.echo("--- More details at https://bit.ly/pio-monitor-filters")
    try:
        miniterm.main(
            default_port=kwargs["port"],
            default_baudrate=kwargs["baud"]
            or ProjectOptions["env.monitor_speed"].default,
            default_rts=kwargs["rts"],
            default_dtr=kwargs["dtr"],
        )
    except Exception as e:
        raise exception.MinitermException(e)


def get_project_options(environment=None):
    config = ProjectConfig.get_instance()
    config.validate(envs=[environment] if environment else None)
    environment = environment or config.get_default_env()
    return config.items(env=environment, as_dict=True)


def apply_project_monitor_options(cli_options, project_options):
    for k in ("port", "speed", "rts", "dtr"):
        k2 = "monitor_%s" % k
        if k == "speed":
            k = "baud"
        if cli_options[k] is None and k2 in project_options:
            cli_options[k] = project_options[k2]
            if k != "port":
                cli_options[k] = int(cli_options[k])
    return cli_options


def project_options_to_monitor_argv(cli_options, project_options, ignore=None):
    confmon_flags = project_options.get("monitor_flags", [])
    result = confmon_flags[::]

    for f in project_options.get("monitor_filters", []):
        result.extend(["--filter", f])

    for k, v in cli_options.items():
        if v is None or (ignore and k in ignore):
            continue
        k = "--" + k.replace("_", "-")
        if k in confmon_flags:
            continue
        if isinstance(v, bool):
            if v:
                result.append(k)
        elif isinstance(v, tuple):
            for i in v:
                result.extend([k, i])
        else:
            result.extend([k, str(v)])
    return result
