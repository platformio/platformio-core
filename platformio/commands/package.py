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
from datetime import datetime

import click

from platformio.clients.registry import RegistryClient
from platformio.package.pack import PackagePacker


def validate_datetime(ctx, param, value):  # pylint: disable=unused-argument
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise click.BadParameter(e)
    return value


@click.group("package", short_help="Package Manager")
def cli():
    pass


@cli.command("pack", short_help="Create a tarball from a package")
@click.argument("package", required=True, metavar="[source directory, tar.gz or zip]")
def package_pack(package):
    p = PackagePacker(package)
    tarball_path = p.pack()
    click.secho('Wrote a tarball to "%s"' % tarball_path, fg="green")


@cli.command(
    "publish", short_help="Publish a package to the PlatformIO Universal Registry"
)
@click.argument("package", required=True, metavar="[source directory, tar.gz or zip]")
@click.option(
    "--owner",
    help="PIO Account username (could be organization username). "
    "Default is set to a username of the authorized PIO Account",
)
@click.option(
    "--released-at",
    callback=validate_datetime,
    help="Custom release date and time in the next format (UTC): 2014-06-13 17:08:52",
)
@click.option("--private", is_flag=True, help="Restricted access (not a public)")
def package_publish(package, owner, released_at, private):
    p = PackagePacker(package)
    archive_path = p.pack()
    response = RegistryClient().publish_package(
        archive_path, owner, released_at, private
    )
    os.remove(archive_path)
    click.secho(response.get("message"), fg="green")
