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

from urllib.parse import quote

import click
from tabulate import tabulate

from platformio import fs, util
from platformio.exception import UserSideException
from platformio.package.manager._registry import PackageManagerRegistryMixin
from platformio.package.meta import PackageSpec, PackageType
from platformio.registry.client import RegistryClient


@click.command("show", short_help="Show package information")
@click.argument("spec", metavar="[<owner>/]<pkg>[@<version>]")
@click.option(
    "-t",
    "--type",
    "pkg_type",
    type=click.Choice(list(PackageType.items().values())),
    help="Package type",
)
def package_show_cmd(spec, pkg_type):
    spec = PackageSpec(spec)
    data = fetch_package_data(spec, pkg_type)
    if not data:
        raise UserSideException(
            "Could not find '%s' package in the PlatormIO Registry" % spec.humanize()
        )

    click.echo()
    click.echo(
        "%s/%s"
        % (
            click.style(data["owner"]["username"], fg="cyan"),
            click.style(data["name"], fg="cyan", bold=True),
        )
    )
    click.echo(
        "%s • %s • %s • Published on %s"
        % (
            data["type"].capitalize(),
            data["version"]["name"],
            "Private" if data.get("private") else "Public",
            util.parse_datetime(data["version"]["released_at"]).strftime("%c"),
        )
    )

    #  Description
    click.echo()
    click.echo(data["description"])

    # Extra info
    click.echo()
    fields = [
        ("homepage", "Homepage"),
        ("repository_url", "Repository"),
        ("license", "License"),
        ("popularity_rank", "Popularity"),
        ("stars_count", "Stars"),
        ("examples_count", "Examples"),
        ("version.unpacked_size", "Installed Size"),
        ("dependents_count", "Used By"),
        ("dependencies_count", "Dependencies"),
        ("platforms", "Compatible Platforms"),
        ("frameworks", "Compatible Frameworks"),
        ("keywords", "Keywords"),
    ]
    type_plural = "libraries" if data["type"] == "library" else (data["type"] + "s")
    extra = [
        (
            "Registry",
            click.style(
                "https://registry.platformio.org/%s/%s/%s"
                % (type_plural, data["owner"]["username"], quote(data["name"])),
                fg="blue",
            ),
        )
    ]
    for key, title in fields:
        if "." in key:
            k1, k2 = key.split(".")
            value = data.get(k1, {}).get(k2)
        else:
            value = data.get(key)
        if not value:
            continue
        if isinstance(value, list):
            value = ", ".join(value)
        elif key.endswith("_size"):
            value = fs.humanize_file_size(value)
        extra.append((title, value))
    click.echo(tabulate(extra))

    # Versions
    click.echo("")
    table = tabulate(
        [
            (
                version["name"],
                fs.humanize_file_size(max(f["size"] for f in version["files"])),
                util.parse_datetime(version["released_at"]),
            )
            for version in data["versions"]
        ],
        headers=["Version", "Size", "Published"],
    )
    click.echo(table)
    click.echo("")


def fetch_package_data(spec, pkg_type=None):
    assert isinstance(spec, PackageSpec)
    client = RegistryClient()
    if pkg_type and spec.owner and spec.name:
        return client.get_package(
            pkg_type, spec.owner, spec.name, version=spec.requirements
        )
    qualifiers = {}
    if spec.id:
        qualifiers["ids"] = str(spec.id)
    if spec.name:
        qualifiers["names"] = spec.name.lower()
    if pkg_type:
        qualifiers["types"] = pkg_type
    if spec.owner:
        qualifiers["owners"] = spec.owner.lower()
    packages = client.list_packages(qualifiers=qualifiers)["items"]
    if not packages:
        return None
    if len(packages) > 1:
        PackageManagerRegistryMixin.print_multi_package_issue(
            click.echo, packages, spec
        )
        return None
    return client.get_package(
        packages[0]["type"],
        packages[0]["owner"]["username"],
        packages[0]["name"],
        version=spec.requirements,
    )
