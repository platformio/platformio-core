# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, style

from platformio.pkgmanager import PackageManager


@command("list", short_help="List installed platforms")
def cli():

    for name, pkgs in PackageManager.get_installed().items():
        echo("{name:<20} with packages: {pkgs}".format(
            name=style(name, fg="cyan"),
            pkgs=", ".join(pkgs.keys())
        ))
