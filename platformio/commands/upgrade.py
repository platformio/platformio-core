# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click
import requests

from platformio import __version__, util
from platformio.exception import GetLatestVersionError


@click.command("upgrade",
               short_help="Upgrade PlatformIO to the latest version")
def cli():
    last = get_latest_version()
    if __version__ == last:
        return click.secho(
            "You're up-to-date!\nPlatformIO %s is currently the "
            "newest version available." % __version__, fg="green"
        )
    else:
        click.secho("Please wait while upgrading PlatformIO ...",
                    fg="yellow")

        pip_result = util.exec_command(["pip", "install", "--upgrade",
                                        "platformio"])
        pio_result = util.exec_command(["platformio", "--version"])

        if last in pio_result['out'].strip():
            click.secho("PlatformIO has been successfully upgraded to %s" %
                        last, fg="green")
        else:
            click.secho(pip_result['out'], fg="green")
            click.secho(pip_result['err'], fg="red")


def get_latest_version():
    try:
        pkgdata = requests.get(
            "https://pypi.python.org/pypi/platformio/json",
            headers=util.get_request_defheaders()
        ).json()
        return pkgdata['info']['version']
    except:
        raise GetLatestVersionError()
