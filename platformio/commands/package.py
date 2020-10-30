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
import tempfile
from datetime import datetime

import click

from platformio import fs
from platformio.clients.registry import RegistryClient
from platformio.compat import ensure_python3
from platformio.package.meta import PackageSpec, PackageType
from platformio.package.pack import PackagePacker


def validate_datetime(ctx, param, value):  # pylint: disable=unused-argument
    if not value:
        return value
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise click.BadParameter(e)
    return value


@click.group("package", short_help="Package manager")
def cli():
    pass


@cli.command("pack", short_help="Create a tarball from a package")
@click.argument(
    "package",
    required=True,
    default=os.getcwd,
    metavar="<source directory, tar.gz or zip>",
)
@click.option(
    "-o", "--output", help="A destination path (folder or a full path to file)"
)
def package_pack(package, output):
    p = PackagePacker(package)
    archive_path = p.pack(output)
    click.secho('Wrote a tarball to "%s"' % archive_path, fg="green")


@cli.command("publish", short_help="Publish a package to the registry")
@click.argument(
    "package",
    required=True,
    default=os.getcwd,
    metavar="<source directory, tar.gz or zip>",
)
@click.option(
    "--owner",
    help="PIO Account username (can be organization username). "
    "Default is set to a username of the authorized PIO Account",
)
@click.option(
    "--released-at",
    callback=validate_datetime,
    help="Custom release date and time in the next format (UTC): 2014-06-13 17:08:52",
)
@click.option("--private", is_flag=True, help="Restricted access (not a public)")
@click.option(
    "--notify/--no-notify",
    default=True,
    help="Notify by email when package is processed",
)
def package_publish(package, owner, released_at, private, notify):
    assert ensure_python3()
    with tempfile.TemporaryDirectory() as tmp_dir:  # pylint: disable=no-member
        with fs.cd(tmp_dir):
            p = PackagePacker(package)
            archive_path = p.pack()
            response = RegistryClient().publish_package(
                archive_path, owner, released_at, private, notify
            )
            os.remove(archive_path)
            click.secho(response.get("message"), fg="green")


@cli.command("unpublish", short_help="Remove a pushed package from the registry")
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
def package_unpublish(package, type, undo):  # pylint: disable=redefined-builtin
    spec = PackageSpec(package)
    response = RegistryClient().unpublish_package(
        type=type,
        name=spec.name,
        owner=spec.owner,
        version=str(spec.requirements),
        undo=undo,
    )
    click.secho(response.get("message"), fg="green")
