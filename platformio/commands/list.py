# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

import click

from platformio.platforms.base import PlatformFactory


@click.command("list", short_help="List installed platforms")
@click.option("--json-output", is_flag=True)
def cli(json_output):

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    installed_platforms.sort()

    data = []
    for platform in installed_platforms:
        p = PlatformFactory.newPlatform(platform)
        data.append({
            "name": platform,
            "packages": p.get_installed_packages()
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        for item in data:
            click.echo("{name:<20} with packages: {pkgs}".format(
                name=click.style(item['name'], fg="cyan"),
                pkgs=", ".join(item['packages'])
            ))
