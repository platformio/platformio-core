# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import re
from os import remove
from os.path import isdir, isfile, join
from shutil import rmtree
from time import time

import click

from platformio import __version__, app, telemetry
from platformio.commands.install import cli as cmd_install
from platformio.commands.lib import lib_update as cmd_libraries_update
from platformio.commands.update import cli as cli_platforms_update
from platformio.commands.upgrade import get_latest_version
from platformio.exception import GetLatestVersionError, UpgraderFailed
from platformio.libmanager import LibraryManager
from platformio.platforms.base import PlatformFactory
from platformio.util import get_home_dir, get_lib_dir


def on_platformio_start(ctx):
    telemetry.on_command(ctx)
    after_upgrade(ctx)
    check_platformio_upgrade()
    check_internal_updates(ctx, "platforms")
    check_internal_updates(ctx, "libraries")


def on_platformio_end(ctx, result):  # pylint: disable=W0613
    pass


def on_platformio_exception(e):
    telemetry.on_exception(e)


class Upgrader(object):

    def __init__(self, from_version, to_version):
        self.from_version = self.version_to_int(from_version)
        self.to_version = self.version_to_int(to_version)

    @staticmethod
    def version_to_int(version):
        intver = int(re.sub(r"[^\d]+", "", version))
        if "dev" in version:
            intver -= 1
        return intver

    def run(self, ctx):
        if self.from_version > self.to_version:
            return True

        result = [True]
        for v in (90, 110):
            if self.from_version >= v:
                continue
            result.append(getattr(self, "_upgrade_to_%d" % v)(ctx))

        return all(result)

    def _upgrade_to_90(self, ctx):  # pylint: disable=R0201
        prev_platforms = []

        # remove platform's folder (obsoleted package structure)
        for name in PlatformFactory.get_platforms().keys():
            pdir = join(get_home_dir(), name)
            if not isdir(pdir):
                continue
            prev_platforms.append(name)
            rmtree(pdir)

        # remove unused files
        for fname in (".pioupgrade", "installed.json"):
            if isfile(join(get_home_dir(), fname)):
                remove(join(get_home_dir(), fname))

        if prev_platforms:
            ctx.invoke(cmd_install, platforms=prev_platforms)

        return True

    def _upgrade_to_110(self, ctx):  # pylint: disable=R0201
        # install "ldscripts" package
        if "titiva" in PlatformFactory.get_platforms(installed=True).keys():
            ctx.invoke(cmd_install, platforms=["titiva"])
        return True


def after_upgrade(ctx):
    if app.get_state_item("last_version", None) == __version__:
        return

    # promotion
    click.echo("\nIf you like %s, please:" % (
        click.style("PlatformIO", fg="cyan")
    ))
    click.echo(
        "- %s us on Twitter to stay up-to-date "
        "on the latest project news > %s" %
        (click.style("follow", fg="cyan"),
         click.style("https://twitter.com/PlatformIO_Org", fg="cyan"))
    )
    click.echo("- %s us a star on GitHub > %s" % (
        click.style("give", fg="cyan"),
        click.style("https://github.com/ivankravets/platformio", fg="cyan")
    ))
    click.secho("Thanks a lot!\n", fg="green")

    last_version = app.get_state_item("last_version", "0.0.0")
    if last_version == "0.0.0":
        return

    click.secho("Please wait while upgrading PlatformIO ...",
                fg="yellow")

    u = Upgrader(last_version, __version__)
    if u.run(ctx):
        app.set_state_item("last_version", __version__)
        click.secho("PlatformIO has been successfully upgraded to %s!\n" %
                    __version__, fg="green")

        telemetry.on_event(category="Auto", action="Upgrade",
                           label="%s > %s" % (last_version, __version__))
    else:
        raise UpgraderFailed()
    click.echo("")


def check_platformio_upgrade():
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_platformio_interval")) * 3600 * 24
    if (time() - interval) < last_check.get("platformio_upgrade", 0):
        return

    last_check['platformio_upgrade'] = int(time())
    app.set_state_item("last_check", last_check)

    try:
        latest_version = get_latest_version()
    except GetLatestVersionError:
        click.secho("Failed to check for PlatformIO upgrades", fg="red")
        return

    if (latest_version == __version__ or
            Upgrader.version_to_int(latest_version) <
            Upgrader.version_to_int(__version__)):
        return

    click.secho("There is a new version %s of PlatformIO available.\n"
                "Please upgrade it via " % latest_version,
                fg="yellow", nl=False)
    click.secho("platformio upgrade", fg="cyan", nl=False)
    click.secho(" command.\nChanges: ", fg="yellow", nl=False)
    click.secho("http://docs.platformio.org/en/latest/history.html\n",
                fg="cyan")


def check_internal_updates(ctx, what):
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_%s_interval" % what)) * 3600 * 24
    if (time() - interval) < last_check.get(what + "_update", 0):
        return

    last_check[what + '_update'] = int(time())
    app.set_state_item("last_check", last_check)

    outdated_items = []
    if what == "platforms":
        for platform in PlatformFactory.get_platforms(installed=True).keys():
            p = PlatformFactory.newPlatform(platform)
            if p.is_outdated():
                outdated_items.append(platform)
    elif what == "libraries":
        lm = LibraryManager(get_lib_dir())
        outdated_items = lm.get_outdated()

    if not outdated_items:
        return

    click.secho("There are the new updates for %s (%s)" %
                (what, ", ".join(outdated_items)), fg="yellow")

    if not app.get_setting("auto_update_" + what):
        click.secho("Please update them via ", fg="yellow", nl=False)
        click.secho("`platformio %supdate`" %
                    ("lib " if what == "libraries" else ""),
                    fg="cyan", nl=False)
        click.secho(" command.\n", fg="yellow")
    else:
        click.secho("Please wait while updating %s ..." % what, fg="yellow")
        if what == "platforms":
            ctx.invoke(cli_platforms_update)
        elif what == "libraries":
            ctx.invoke(cmd_libraries_update)
        click.echo()

        telemetry.on_event(category="Auto", action="Update",
                           label=what.title())
