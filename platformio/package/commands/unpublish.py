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

from platformio.account.client import AccountClient
from platformio.package.meta import PackageSpec, PackageType
from platformio.registry.client import RegistryClient


@click.command("unpublish", short_help="Remove a pushed package from the registry")
@click.argument(
    "package", required=True, metavar="[<organization>/]<pkgname>[@<version>]"
)
@click.option(
    "--type",
    type=click.Choice(list(PackageType.items().values())),
    default="library",
    help="Package type, default is set to `library`",
)
@click.option(
    "--undo",
    is_flag=True,
    help="Undo a remove, putting a version back into the registry",
)
def package_unpublish_cmd(package, type, undo):  # pylint: disable=redefined-builtin
    spec = PackageSpec(package)
    response = RegistryClient().unpublish_package(
        owner=spec.owner or AccountClient().get_logged_username(),
        type=type,
        name=spec.name,
        version=str(spec.requirements),
        undo=undo,
    )
    click.secho(response.get("message"), fg="green")
