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

from os import getenv
from os.path import join
from time import time

import click
import semantic_version

from platformio import __version__, app, exception, fs, telemetry, util
from platformio.commands import PlatformioCLI
from platformio.commands.lib import CTX_META_STORAGE_DIRS_KEY
from platformio.commands.lib import lib_update as cmd_lib_update
from platformio.commands.platform import platform_update as cmd_platform_update
from platformio.commands.upgrade import get_latest_version
from platformio.managers.core import update_core_packages
from platformio.managers.lib import LibraryManager
from platformio.managers.platform import PlatformFactory, PlatformManager
from platformio.proc import is_ci, is_container


def on_platformio_start(ctx, force, caller):
    app.set_session_var("command_ctx", ctx)
    app.set_session_var("force_option", force)
    set_caller(caller)
    telemetry.on_command()

    if not PlatformioCLI.in_silence():
        after_upgrade(ctx)


def on_platformio_end(ctx, result):  # pylint: disable=unused-argument
    if PlatformioCLI.in_silence():
        return

    try:
        check_platformio_upgrade()
        check_internal_updates(ctx, "platforms")
        check_internal_updates(ctx, "libraries")
    except (
        exception.InternetIsOffline,
        exception.GetLatestVersionError,
        exception.APIRequestError,
    ):
        click.secho(
            "Failed to check for PlatformIO upgrades. "
            "Please check your Internet connection.",
            fg="red",
        )


def on_platformio_exception(e):
    telemetry.on_exception(e)


def set_caller(caller=None):
    if not caller:
        if getenv("PLATFORMIO_CALLER"):
            caller = getenv("PLATFORMIO_CALLER")
        elif getenv("VSCODE_PID") or getenv("VSCODE_NLS_CONFIG"):
            caller = "vscode"
        elif is_container():
            if getenv("C9_UID"):
                caller = "C9"
            elif getenv("USER") == "cabox":
                caller = "CA"
            elif getenv("CHE_API", getenv("CHE_API_ENDPOINT")):
                caller = "Che"
    app.set_session_var("caller_id", caller)


class Upgrader(object):
    def __init__(self, from_version, to_version):
        self.from_version = semantic_version.Version.coerce(
            util.pepver_to_semver(from_version)
        )
        self.to_version = semantic_version.Version.coerce(
            util.pepver_to_semver(to_version)
        )

        self._upgraders = [
            (semantic_version.Version("3.5.0-a.2"), self._update_dev_platforms)
        ]

    def run(self, ctx):
        if self.from_version > self.to_version:
            return True

        result = [True]
        for version, callback in self._upgraders:
            if self.from_version >= version or self.to_version < version:
                continue
            result.append(callback(ctx))

        return all(result)

    @staticmethod
    def _update_dev_platforms(ctx):
        ctx.invoke(cmd_platform_update)
        return True


def after_upgrade(ctx):
    terminal_width, _ = click.get_terminal_size()
    last_version = app.get_state_item("last_version", "0.0.0")
    if last_version == __version__:
        return

    if last_version == "0.0.0":
        app.set_state_item("last_version", __version__)
    elif semantic_version.Version.coerce(
        util.pepver_to_semver(last_version)
    ) > semantic_version.Version.coerce(util.pepver_to_semver(__version__)):
        click.secho("*" * terminal_width, fg="yellow")
        click.secho(
            "Obsolete PIO Core v%s is used (previous was %s)"
            % (__version__, last_version),
            fg="yellow",
        )
        click.secho("Please remove multiple PIO Cores from a system:", fg="yellow")
        click.secho(
            "https://docs.platformio.org/page/faq.html"
            "#multiple-pio-cores-in-a-system",
            fg="cyan",
        )
        click.secho("*" * terminal_width, fg="yellow")
        return
    else:
        click.secho("Please wait while upgrading PlatformIO...", fg="yellow")
        app.clean_cache()

        # Update PlatformIO's Core packages
        update_core_packages(silent=True)

        u = Upgrader(last_version, __version__)
        if u.run(ctx):
            app.set_state_item("last_version", __version__)
            click.secho(
                "PlatformIO has been successfully upgraded to %s!\n" % __version__,
                fg="green",
            )
            telemetry.send_event(
                category="Auto",
                action="Upgrade",
                label="%s > %s" % (last_version, __version__),
            )
        else:
            raise exception.UpgradeError("Auto upgrading...")
        click.echo("")

    # PlatformIO banner
    click.echo("*" * terminal_width)
    click.echo("If you like %s, please:" % (click.style("PlatformIO", fg="cyan")))
    click.echo(
        "- %s us on Twitter to stay up-to-date "
        "on the latest project news > %s"
        % (
            click.style("follow", fg="cyan"),
            click.style("https://twitter.com/PlatformIO_Org", fg="cyan"),
        )
    )
    click.echo(
        "- %s it on GitHub > %s"
        % (
            click.style("star", fg="cyan"),
            click.style("https://github.com/platformio/platformio", fg="cyan"),
        )
    )
    if not getenv("PLATFORMIO_IDE"):
        click.echo(
            "- %s PlatformIO IDE for embedded development > %s"
            % (
                click.style("try", fg="cyan"),
                click.style("https://platformio.org/platformio-ide", fg="cyan"),
            )
        )
    if not is_ci():
        click.echo(
            "- %s us with PlatformIO Plus > %s"
            % (
                click.style("support", fg="cyan"),
                click.style("https://pioplus.com", fg="cyan"),
            )
        )

    click.echo("*" * terminal_width)
    click.echo("")


def check_platformio_upgrade():
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_platformio_interval")) * 3600 * 24
    if (time() - interval) < last_check.get("platformio_upgrade", 0):
        return

    last_check["platformio_upgrade"] = int(time())
    app.set_state_item("last_check", last_check)

    util.internet_on(raise_exception=True)

    # Update PlatformIO's Core packages
    update_core_packages(silent=True)

    latest_version = get_latest_version()
    if semantic_version.Version.coerce(
        util.pepver_to_semver(latest_version)
    ) <= semantic_version.Version.coerce(util.pepver_to_semver(__version__)):
        return

    terminal_width, _ = click.get_terminal_size()

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho(
        "There is a new version %s of PlatformIO available.\n"
        "Please upgrade it via `" % latest_version,
        fg="yellow",
        nl=False,
    )
    if getenv("PLATFORMIO_IDE"):
        click.secho("PlatformIO IDE Menu: Upgrade PlatformIO", fg="cyan", nl=False)
        click.secho("`.", fg="yellow")
    elif join("Cellar", "platformio") in fs.get_source_dir():
        click.secho("brew update && brew upgrade", fg="cyan", nl=False)
        click.secho("` command.", fg="yellow")
    else:
        click.secho("platformio upgrade", fg="cyan", nl=False)
        click.secho("` or `", fg="yellow", nl=False)
        click.secho("pip install -U platformio", fg="cyan", nl=False)
        click.secho("` command.", fg="yellow")
    click.secho("Changes: ", fg="yellow", nl=False)
    click.secho("https://docs.platformio.org/en/latest/history.html", fg="cyan")
    click.echo("*" * terminal_width)
    click.echo("")


def check_internal_updates(ctx, what):
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_%s_interval" % what)) * 3600 * 24
    if (time() - interval) < last_check.get(what + "_update", 0):
        return

    last_check[what + "_update"] = int(time())
    app.set_state_item("last_check", last_check)

    util.internet_on(raise_exception=True)

    pm = PlatformManager() if what == "platforms" else LibraryManager()
    outdated_items = []
    for manifest in pm.get_installed():
        if manifest["name"] in outdated_items:
            continue
        conds = [
            pm.outdated(manifest["__pkg_dir"]),
            what == "platforms"
            and PlatformFactory.newPlatform(
                manifest["__pkg_dir"]
            ).are_outdated_packages(),
        ]
        if any(conds):
            outdated_items.append(manifest["name"])

    if not outdated_items:
        return

    terminal_width, _ = click.get_terminal_size()

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho(
        "There are the new updates for %s (%s)" % (what, ", ".join(outdated_items)),
        fg="yellow",
    )

    if not app.get_setting("auto_update_" + what):
        click.secho("Please update them via ", fg="yellow", nl=False)
        click.secho(
            "`platformio %s update`"
            % ("lib --global" if what == "libraries" else "platform"),
            fg="cyan",
            nl=False,
        )
        click.secho(" command.\n", fg="yellow")
        click.secho(
            "If you want to manually check for the new versions "
            "without updating, please use ",
            fg="yellow",
            nl=False,
        )
        click.secho(
            "`platformio %s update --dry-run`"
            % ("lib --global" if what == "libraries" else "platform"),
            fg="cyan",
            nl=False,
        )
        click.secho(" command.", fg="yellow")
    else:
        click.secho("Please wait while updating %s ..." % what, fg="yellow")
        if what == "platforms":
            ctx.invoke(cmd_platform_update, platforms=outdated_items)
        elif what == "libraries":
            ctx.meta[CTX_META_STORAGE_DIRS_KEY] = [pm.package_dir]
            ctx.invoke(cmd_lib_update, libraries=outdated_items)
        click.echo()

        telemetry.send_event(category="Auto", action="Update", label=what.title())

    click.echo("*" * terminal_width)
    click.echo("")
