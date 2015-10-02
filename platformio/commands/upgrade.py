# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click
import requests

from platformio import __version__, exception, util


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

        cmds = (
            ["pip", "install", "--upgrade", "pip", "setuptools"],
            ["pip", "install", "--upgrade", "platformio"],
            ["platformio", "--version"]
        )

        cmd = None
        r = None
        try:
            for cmd in cmds:
                r = None
                r = util.exec_command(cmd)

                # try pip with disabled cache
                if r['returncode'] != 0 and cmd[0] == "pip":
                    r = util.exec_command(["pip", "--no-cache-dir"] + cmd[1:])

                assert r['returncode'] == 0
            assert last in r['out'].strip()
            click.secho(
                "PlatformIO has been successfully upgraded to %s" % last,
                fg="green")
            click.echo("Release notes: ", nl=False)
            click.secho("http://docs.platformio.org/en/latest/history.html",
                        fg="cyan")
        except (OSError, AssertionError) as e:
            if not r:
                raise exception.PlatformioUpgradeError(
                    "\n".join([str(cmd), str(e)]))
            if ("Permission denied" in r['err'] and
                    "windows" not in util.get_systype()):
                click.secho("""
-----------------
Permission denied
-----------------
You need the `sudo` permission to install Python packages. Try

> sudo platformio upgrade

WARNING! Don't use `sudo` for the rest PlatformIO commands.
""", fg="yellow", err=True)
                raise exception.ReturnErrorCode()
            else:
                raise exception.PlatformioUpgradeError(
                    "\n".join([str(cmd), r['out'], r['err']]))


def get_latest_version():
    try:
        pkgdata = requests.get(
            "https://pypi.python.org/pypi/platformio/json",
            headers=util.get_request_defheaders()
        ).json()
        return pkgdata['info']['version']
    except:
        raise exception.GetLatestVersionError()
