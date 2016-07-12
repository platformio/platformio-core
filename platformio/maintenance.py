# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

import re
import struct
from os import getenv, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from time import time

import click

from platformio import __version__, app, exception, telemetry, util
from platformio.commands.lib import lib_update as cmd_libraries_update
from platformio.commands.platforms import \
    platforms_install as cmd_platforms_install
from platformio.commands.platforms import \
    platforms_update as cmd_platforms_update
from platformio.commands.upgrade import get_latest_version
from platformio.libmanager import LibraryManager
from platformio.platforms.base import PlatformFactory
from platformio.util import get_home_dir


def in_silence(ctx):
    ctx_args = ctx.args or []
    return (ctx_args and
            (ctx.args[0] == "upgrade" or "--json-output" in ctx_args))


def on_platformio_start(ctx, force, caller):
    app.set_session_var("command_ctx", ctx)
    app.set_session_var("force_option", force)
    app.set_session_var("caller_id", caller)
    telemetry.on_command()

    if not in_silence(ctx):
        after_upgrade(ctx)


def on_platformio_end(ctx, result):  # pylint: disable=W0613
    if in_silence(ctx):
        return

    try:
        check_platformio_upgrade()
        check_internal_updates(ctx, "platforms")
        check_internal_updates(ctx, "libraries")
    except (exception.GetLatestVersionError, exception.APIRequestError):
        click.secho("Failed to check for PlatformIO upgrades. "
                    "Please check your Internet connection.", fg="red")


def on_platformio_exception(e):
    telemetry.on_exception(e)


class Upgrader(object):

    def __init__(self, from_version, to_version):
        self.from_version = self.version_to_int(from_version)
        self.to_version = self.version_to_int(to_version)

        self._upgraders = (
            (self.version_to_int("0.9.0"), self._upgrade_to_0_9_0),
            (self.version_to_int("1.0.0"), self._upgrade_to_1_0_0)
        )

    @staticmethod
    def version_to_int(version):
        match = re.match(r"(\d+)\.(\d+)\.(\d+)(\D+)?", version)
        assert match is not None and len(match.groups()) is 4
        verchrs = [chr(int(match.group(i))) for i in range(1, 4)]
        verchrs.append(chr(255 if match.group(4) is None else 0))
        return struct.unpack(">I", "".join(verchrs))

    def run(self, ctx):
        if self.from_version > self.to_version:
            return True

        result = [True]
        for item in self._upgraders:
            if self.from_version >= item[0]:
                continue
            result.append(item[1](ctx))

        return all(result)

    def _upgrade_to_0_9_0(self, ctx):  # pylint: disable=R0201
        prev_platforms = []

        # remove platform's folder (obsolete package structure)
        for name in PlatformFactory.get_platforms():
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
            ctx.invoke(cmd_platforms_install, platforms=prev_platforms)

        return True

    def _upgrade_to_1_0_0(self, ctx):  # pylint: disable=R0201
        installed_platforms = PlatformFactory.get_platforms(
            installed=True).keys()
        if installed_platforms:
            ctx.invoke(cmd_platforms_install, platforms=installed_platforms)
        return True


def after_upgrade(ctx):
    last_version = app.get_state_item("last_version", "0.0.0")
    if last_version == __version__:
        return

    terminal_width, _ = click.get_terminal_size()

    # promotion
    click.echo("")
    click.echo("*" * terminal_width)
    click.echo("If you like %s, please:" % (
        click.style("PlatformIO", fg="cyan")
    ))
    click.echo(
        "- %s us on Twitter to stay up-to-date "
        "on the latest project news > %s" %
        (click.style("follow", fg="cyan"),
         click.style("https://twitter.com/PlatformIO_Org", fg="cyan"))
    )
    click.echo("- %s it on GitHub > %s" % (
        click.style("star", fg="cyan"),
        click.style("https://github.com/platformio/platformio", fg="cyan")
    ))
    if not getenv("PLATFORMIO_IDE"):
        click.echo("- %s PlatformIO IDE for IoT development > %s" % (
            click.style("try", fg="cyan"),
            click.style("http://platformio.org/platformio-ide", fg="cyan")
        ))
    if not util.is_ci():
        click.echo("- %s to keep PlatformIO alive! > %s" % (
            click.style("donate", fg="cyan"),
            click.style("http://platformio.org/donate", fg="cyan")
        ))

    click.echo("*" * terminal_width)
    click.echo("")

    if last_version == "0.0.0":
        app.set_state_item("last_version", __version__)
        return

    click.secho("Please wait while upgrading PlatformIO ...",
                fg="yellow")

    u = Upgrader(last_version, __version__)
    if u.run(ctx):
        app.set_state_item("last_version", __version__)
        ctx.invoke(cmd_platforms_update)

        click.secho("PlatformIO has been successfully upgraded to %s!\n" %
                    __version__, fg="green")

        telemetry.on_event(category="Auto", action="Upgrade",
                           label="%s > %s" % (last_version, __version__))
    else:
        raise exception.UpgradeError("Auto upgrading...")
    click.echo("")


def check_platformio_upgrade():
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_platformio_interval")) * 3600 * 24
    if (time() - interval) < last_check.get("platformio_upgrade", 0):
        return

    last_check['platformio_upgrade'] = int(time())
    app.set_state_item("last_check", last_check)

    latest_version = get_latest_version()
    if (latest_version == __version__ or
            Upgrader.version_to_int(latest_version) <
            Upgrader.version_to_int(__version__)):
        return

    terminal_width, _ = click.get_terminal_size()

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho("There is a new version %s of PlatformIO available.\n"
                "Please upgrade it via `" % latest_version,
                fg="yellow", nl=False)
    if getenv("PLATFORMIO_IDE"):
        click.secho("PlatformIO IDE Menu: Upgrade PlatformIO",
                    fg="cyan", nl=False)
        click.secho("`.", fg="yellow")
    else:
        click.secho("platformio upgrade", fg="cyan", nl=False)
        click.secho("` or `", fg="yellow", nl=False)
        click.secho("pip install -U platformio", fg="cyan", nl=False)
        click.secho("` command.", fg="yellow")
    click.secho("Changes: ", fg="yellow", nl=False)
    click.secho("http://docs.platformio.org/en/latest/history.html",
                fg="cyan")
    click.echo("*" * terminal_width)
    click.echo("")


def check_internal_updates(ctx, what):
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_%s_interval" % what)) * 3600 * 24
    if (time() - interval) < last_check.get(what + "_update", 0):
        return

    last_check[what + '_update'] = int(time())
    app.set_state_item("last_check", last_check)

    outdated_items = []
    if what == "platforms":
        for platform in PlatformFactory.get_platforms(installed=True):
            p = PlatformFactory.newPlatform(platform)
            if p.is_outdated():
                outdated_items.append(platform)
    elif what == "libraries":
        lm = LibraryManager()
        outdated_items = lm.get_outdated()

    if not outdated_items:
        return

    terminal_width, _ = click.get_terminal_size()

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho("There are the new updates for %s (%s)" %
                (what, ", ".join(outdated_items)), fg="yellow")

    if not app.get_setting("auto_update_" + what):
        click.secho("Please update them via ", fg="yellow", nl=False)
        click.secho("`platformio %s update`" %
                    ("lib" if what == "libraries" else "platforms"),
                    fg="cyan", nl=False)
        click.secho(" command.", fg="yellow")
    else:
        click.secho("Please wait while updating %s ..." % what, fg="yellow")
        if what == "platforms":
            ctx.invoke(cmd_platforms_update)
        elif what == "libraries":
            ctx.invoke(cmd_libraries_update)
        click.echo()

        telemetry.on_event(category="Auto", action="Update",
                           label=what.title())

    click.echo("*" * terminal_width)
    click.echo("")
