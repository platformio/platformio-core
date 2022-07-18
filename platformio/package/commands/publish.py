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
import tarfile
import tempfile
from datetime import datetime

import click
from tabulate import tabulate

from platformio import fs
from platformio.account.client import AccountClient
from platformio.compat import isascii
from platformio.exception import UserSideException
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.manifest.schema import ManifestSchema
from platformio.package.meta import PackageType
from platformio.package.pack import PackagePacker
from platformio.package.unpack import FileUnpacker, TARArchiver
from platformio.registry.client import RegistryClient


def validate_datetime(ctx, param, value):  # pylint: disable=unused-argument
    if not value:
        return value
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise click.BadParameter(exc)
    return value


@click.command("publish", short_help="Publish a package to the registry")
@click.argument(
    "package",
    default=os.getcwd,
    metavar="<source directory, tar.gz or zip>",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "--owner",
    help="PIO Account username (can be organization username). "
    "Default is set to a username of the authorized PIO Account",
)
@click.option(
    "--type",
    "type_",
    type=click.Choice(list(PackageType.items().values())),
    help="Custom package type",
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
    "--no-interactive",
    is_flag=True,
    help="Do not show interactive prompt",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Do not show interactive prompt",
    hidden=True,
)
def package_publish_cmd(  # pylint: disable=too-many-arguments, too-many-locals
    package, owner, type_, released_at, private, notify, no_interactive, non_interactive
):
    click.secho("Preparing a package...", fg="cyan")
    no_interactive = no_interactive or non_interactive
    owner = owner or AccountClient().get_logged_username()
    do_not_pack = (
        not os.path.isdir(package)
        and isinstance(FileUnpacker.new_archiver(package), TARArchiver)
        and PackageType.from_archive(package)
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

        type_ = type_ or PackageType.from_archive(archive_path)
        manifest = ManifestSchema().load_manifest(
            ManifestParserFactory.new_from_archive(archive_path).as_dict()
        )
        name = manifest.get("name")
        version = manifest.get("version")
        data = [
            ("Type:", type_),
            ("Owner:", owner),
            ("Name:", name),
            ("Version:", version),
            ("Size:", fs.humanize_file_size(os.path.getsize(archive_path))),
        ]
        if manifest.get("system"):
            data.insert(len(data) - 1, ("System:", ", ".join(manifest.get("system"))))
        click.echo(tabulate(data, tablefmt="plain"))

        # check files containing non-ascii chars
        check_archive_file_names(archive_path)

        # look for duplicates
        check_package_duplicates(owner, type_, name, version, manifest.get("system"))

        if not no_interactive:
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

        click.secho(
            "The package publishing may take some time depending "
            "on your Internet connection and the package size.",
            fg="yellow",
        )
        click.echo("Publishing...")
        response = RegistryClient().publish_package(
            owner, type_, archive_path, released_at, private, notify
        )
        if not do_not_pack:
            os.remove(archive_path)
        click.secho(response.get("message"), fg="green")


def check_archive_file_names(archive_path):
    with tarfile.open(archive_path, mode="r:gz") as tf:
        for name in tf.getnames():
            if not isascii(name) or not name.isprintable():
                click.secho(
                    f"Warning! The `{name}` file contains non-ASCII chars and can "
                    "lead to the unpacking issues on a user machine",
                    fg="yellow",
                )


def check_package_duplicates(
    owner, type, name, version, system
):  # pylint: disable=redefined-builtin
    found = False
    items = (
        RegistryClient()
        .list_packages(qualifiers=dict(types=[type], names=[name]))
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
