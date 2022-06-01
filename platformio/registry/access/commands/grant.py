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

import click

from platformio.registry.access.validate import validate_client, validate_urn
from platformio.registry.client import RegistryClient


@click.command("grant", short_help="Grant access")
@click.argument("level", type=click.Choice(["admin", "maintainer", "guest"]))
@click.argument(
    "client",
    metavar="[<ORGNAME:TEAMNAME>|<USERNAME>]",
    callback=lambda _, __, value: validate_client(value),
)
@click.argument(
    "urn",
    callback=lambda _, __, value: validate_urn(value),
)
@click.option("--urn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_grant_cmd(level, client, urn, urn_type):  # pylint: disable=unused-argument
    reg_client = RegistryClient()
    reg_client.grant_access_for_resource(urn=urn, client=client, level=level)
    return click.secho(
        "Access for resource %s has been granted for %s" % (urn, client),
        fg="green",
    )
