# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, secho
from requests import get

from platformio import __version__
from platformio.exception import GetLatestVersionError
from platformio.util import exec_command


@command("upgrade", short_help="Upgrade PlatformIO to the latest version")
def cli():
    try:
        last = get_latest_version()
    except:
        raise GetLatestVersionError()

    if __version__ == last:
        return secho("You're up-to-date!\nPlatformIO %s is currently the "
                     "newest version available." % __version__, fg="green")
    else:
        result = exec_command(["pip", "install", "--upgrade", "platformio"])
        secho(result['out'], fg="green")
        secho(result['err'], fg="red")


def get_latest_version():
    pkgdata = get("https://pypi.python.org/pypi/platformio/json").json()
    return pkgdata['info']['version']
