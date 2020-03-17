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
from fnmatch import fnmatch

import click
from serial.tools import miniterm

from platformio import exception, fs, util
from platformio.commands.device import helpers as device_helpers
from platformio.compat import dump_json_to_unicode
from platformio.managers.platform import PlatformFactory
from platformio.project.exception import NotPlatformIOProjectError


@click.group(short_help="Monitor device or list existing")
def cli():
    pass


@cli.command("list", short_help="List devices")
@click.option("--serial", is_flag=True, help="List serial ports, default")
@click.option("--logical", is_flag=True, help="List logical devices")
@click.option("--mdns", is_flag=True, help="List multicast DNS services")
@click.option("--json-output", is_flag=True)
def device_list(  # pylint: disable=too-many-branches
    serial, logical, mdns, json_output
):
    if not logical and not mdns:
        serial = True
    data = {}
    if serial:
        data["serial"] = util.get_serial_ports()
    if logical:
        data["logical"] = util.get_logical_devices()
    if mdns:
        data["mdns"] = util.get_mdns_services()

    single_key = list(data)[0] if len(list(data)) == 1 else None

    if json_output:
        return click.echo(
            dump_json_to_unicode(data[single_key] if single_key else data)
        )

    titles = {
        "serial": "Serial Ports",
        "logical": "Logical Devices",
        "mdns": "Multicast DNS Services",
    }

    for key, value in data.items():
        if not single_key:
            click.secho(titles[key], bold=True)
            click.echo("=" * len(titles[key]))

        if key == "serial":
            for item in value:
                click.secho(item["port"], fg="cyan")
                click.echo("-" * len(item["port"]))
                click.echo("Hardware ID: %s" % item["hwid"])
                click.echo("Description: %s" % item["description"])
                click.echo("")

        if key == "logical":
            for item in value:
                click.secho(item["path"], fg="cyan")
                click.echo("-" * len(item["path"]))
                click.echo("Name: %s" % item["name"])
                click.echo("")

        if key == "mdns":
            for item in value:
                click.secho(item["name"], fg="cyan")
                click.echo("-" * len(item["name"]))
                click.echo("Type: %s" % item["type"])
                click.echo("IP: %s" % item["ip"])
                click.echo("Port: %s" % item["port"])
                if item["properties"]:
                    click.echo(
                        "Properties: %s"
                        % (
                            "; ".join(
                                [
                                    "%s=%s" % (k, v)
                                    for k, v in item["properties"].items()
                                ]
                            )
                        )
                    )
                click.echo("")

        if single_key:
            click.echo("")

    return True


@cli.command("monitor", short_help="Monitor device (Serial)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option("--baud", "-b", type=int, help="Set baud rate, default=9600")
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
def device_monitor(**kwargs):  # pylint: disable=too-many-branches
    # load default monitor filters
    filters_dir = os.path.join(fs.get_source_dir(), "commands", "device", "filters")
    for name in os.listdir(filters_dir):
        if not name.endswith(".py"):
            continue
        device_helpers.load_monitor_filter(os.path.join(filters_dir, name))

    project_options = {}
    try:
        with fs.cd(kwargs["project_dir"]):
            project_options = device_helpers.get_project_options(kwargs["environment"])
        kwargs = device_helpers.apply_project_monitor_options(kwargs, project_options)
    except NotPlatformIOProjectError:
        pass

    platform = None
    if "platform" in project_options:
        with fs.cd(kwargs["project_dir"]):
            platform = PlatformFactory.newPlatform(project_options["platform"])
            device_helpers.register_platform_filters(
                platform, kwargs["project_dir"], kwargs["environment"]
            )

    if not kwargs["port"]:
        ports = util.get_serial_ports(filter_hwid=True)
        if len(ports) == 1:
            kwargs["port"] = ports[0]["port"]
        elif "platform" in project_options and "board" in project_options:
            board_hwids = device_helpers.get_board_hwids(
                kwargs["project_dir"], platform, project_options["board"],
            )
            for item in ports:
                for hwid in board_hwids:
                    hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                    if hwid_str in item["hwid"]:
                        kwargs["port"] = item["port"]
                        break
                if kwargs["port"]:
                    break
    elif kwargs["port"] and (set(["*", "?", "[", "]"]) & set(kwargs["port"])):
        for item in util.get_serial_ports():
            if fnmatch(item["port"], kwargs["port"]):
                kwargs["port"] = item["port"]
                break

    # override system argv with patched options
    sys.argv = ["monitor"] + device_helpers.options_to_argv(
        kwargs,
        project_options,
        ignore=("port", "baud", "rts", "dtr", "environment", "project_dir"),
    )

    if not kwargs["quiet"]:
        click.echo(
            "--- Available filters and text transformations: %s"
            % ", ".join(sorted(miniterm.TRANSFORMATIONS.keys()))
        )
        click.echo("--- More details at http://bit.ly/pio-monitor-filters")
    try:
        miniterm.main(
            default_port=kwargs["port"],
            default_baudrate=kwargs["baud"] or 9600,
            default_rts=kwargs["rts"],
            default_dtr=kwargs["dtr"],
        )
    except Exception as e:
        raise exception.MinitermException(e)
