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
from tabulate import tabulate

from platformio import fs
from platformio.clients.account import AccountClient
from platformio.clients.registry import RegistryClient
from platformio.exception import UserSideException
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.manifest.schema import ManifestSchema, ManifestValidationError
from platformio.package.meta import PackageSpec, PackageType
from platformio.package.pack import PackagePacker
from platformio.package.unpack import FileUnpacker, TARArchiver


def validate_datetime(ctx, param, value):  # pylint: disable=unused-argument
    if not value:
        return value
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise click.BadParameter(e)
    return value


def load_manifest_from_archive(path):
    return ManifestSchema().load_manifest(
        ManifestParserFactory.new_from_archive(path).as_dict()
    )


def check_package_duplicates(
    owner, type, name, version, system
):  # pylint: disable=redefined-builtin
    found = False
    items = (
        RegistryClient()
        .list_packages(filters=dict(types=[type], names=[name]))
        .get("items")
    )
    if not items:
        return True
    # duplicated version by owner / system
    found = False
    for item in items:
        if item["owner"]["username"] != owner or item["version"]["name"] != version:
            continue
        if not system:
            found = True
            break
        published_systems = []
        for f in item["version"]["files"]:
            published_systems.extend(f.get("system", []))
        found = set(system).issubset(set(published_systems))
    if found:
        raise UserSideException(
            "The package `%s/%s@%s` is already published in the registry"
            % (owner, name, version)
        )
    other_owners = [
        item["owner"]["username"]
        for item in items
        if item["owner"]["username"] != owner
    ]
    if other_owners:
        click.secho(
            "\nWarning! A package with the name `%s` is already published by the next "
            "owners: %s\n" % (name, ", ".join(other_owners)),
            fg="yellow",
        )
    return True


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
    # validate manifest
    try:
        load_manifest_from_archive(archive_path)
    except ManifestValidationError as e:
        os.remove(archive_path)
        raise e
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
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Do not show interactive prompt",
)
def package_publish(  # pylint: disable=too-many-arguments, too-many-locals
    package, owner, released_at, private, notify, non_interactive
):
    click.secho("Preparing a package...", fg="cyan")
    owner = owner or AccountClient().get_logged_username()
    do_not_pack = not os.path.isdir(package) and isinstance(
        FileUnpacker.new_archiver(package), TARArchiver
    )
    archive_path = None
    with tempfile.TemporaryDirectory() as tmp_dir:  # pylint: disable=no-member
        # publish .tar.gz instantly without repacking
        if do_not_pack:
            archive_path = package
        else:
            with fs.cd(tmp_dir):
                p = PackagePacker(package)
                archive_path = p.pack()

        type_ = PackageType.from_archive(archive_path)
        manifest = load_manifest_from_archive(archive_path)
        name = manifest.get("name")
        version = manifest.get("version")
        data = [
            ("Type:", type_),
            ("Owner:", owner),
            ("Name:", name),
            ("Version:", version),
        ]
        if manifest.get("system"):
            data.insert(len(data) - 1, ("System:", ", ".join(manifest.get("system"))))
        click.echo(tabulate(data, tablefmt="plain"))

        # look for duplicates
        check_package_duplicates(owner, type_, name, version, manifest.get("system"))

        if not non_interactive:
            click.confirm(
                "Are you sure you want to publish the %s %s to the registry?\n"
                % (
                    type_,
                    click.style(
                        "%s/%s@%s" % (owner, name, version),
                        fg="cyan",
                    ),
                ),
                abort=True,
            )

        response = RegistryClient().publish_package(
            owner, type_, archive_path, released_at, private, notify
        )
        if not do_not_pack:
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
        owner=spec.owner or AccountClient().get_logged_username(),
        type=type,
        name=spec.name,
        version=str(spec.requirements),
        undo=undo,
    )
    click.secho(response.get("message"), fg="green")
