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

import json

import click

from platformio.device.list.util import (
    list_logical_devices,
    list_mdns_services,
    list_serial_ports,
)


@click.command("list", short_help="List devices")
@click.option("--serial", is_flag=True, help="List serial ports, default")
@click.option("--logical", is_flag=True, help="List logical devices")
@click.option("--mdns", is_flag=True, help="List multicast DNS services")
@click.option("--json-output", is_flag=True)
def device_list_cmd(  # pylint: disable=too-many-branches
    serial, logical, mdns, json_output
):
    if not logical and not mdns:
        serial = True
    data = {}
    if serial:
        data["serial"] = list_serial_ports()
    if logical:
        data["logical"] = list_logical_devices()
    if mdns:
        data["mdns"] = list_mdns_services()

    single_key = list(data)[0] if len(list(data)) == 1 else None

    if json_output:
        return click.echo(json.dumps(data[single_key] if single_key else data))

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
