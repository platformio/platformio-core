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
import shutil
from time import time

import click
import semantic_version

from platformio import __version__, app, exception, fs, telemetry
from platformio.cache import cleanup_content_cache
from platformio.clients import http
from platformio.commands import PlatformioCLI
from platformio.commands.lib.command import CTX_META_STORAGE_DIRS_KEY
from platformio.commands.lib.command import lib_update as cmd_lib_update
from platformio.commands.platform import platform_update as cmd_platform_update
from platformio.commands.system.prune import calculate_unnecessary_system_data
from platformio.commands.upgrade import get_latest_version
from platformio.package.manager.core import update_core_packages
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.package.version import pepver_to_semver
from platformio.platform.factory import PlatformFactory
from platformio.proc import is_container


def on_platformio_start(ctx, force, caller):
    app.set_session_var("command_ctx", ctx)
    app.set_session_var("force_option", force)
    set_caller(caller)
    telemetry.on_command()

    if PlatformioCLI.in_silence():
        return
    after_upgrade(ctx)


def on_platformio_end(ctx, result):  # pylint: disable=unused-argument
    if PlatformioCLI.in_silence():
        return

    try:
        check_platformio_upgrade()
        check_internal_updates(ctx, "platforms")
        check_internal_updates(ctx, "libraries")
        check_prune_system()
    except (
        http.HTTPClientError,
        http.InternetIsOffline,
        exception.GetLatestVersionError,
    ):
        click.secho(
            "Failed to check for PlatformIO upgrades. "
            "Please check your Internet connection.",
            fg="red",
        )


def on_platformio_exception(e):
    telemetry.on_exception(e)


def set_caller(caller=None):
    caller = caller or os.getenv("PLATFORMIO_CALLER")
    if caller:
        return app.set_session_var("caller_id", caller)
    if os.getenv("VSCODE_PID") or os.getenv("VSCODE_NLS_CONFIG"):
        caller = "vscode"
    elif os.getenv("GITPOD_INSTANCE_ID") or os.getenv("GITPOD_WORKSPACE_URL"):
        caller = "gitpod"
    elif is_container():
        if os.getenv("C9_UID"):
            caller = "C9"
        elif os.getenv("USER") == "cabox":
            caller = "CA"
        elif os.getenv("CHE_API", os.getenv("CHE_API_ENDPOINT")):
            caller = "Che"
    return app.set_session_var("caller_id", caller)


class Upgrader(object):
    def __init__(self, from_version, to_version):
        self.from_version = pepver_to_semver(from_version)
        self.to_version = pepver_to_semver(to_version)

        self._upgraders = [
            (semantic_version.Version("3.5.0-a.2"), self._update_dev_platforms),
            (semantic_version.Version("4.4.0-a.8"), self._update_pkg_metadata),
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

    @staticmethod
    def _update_pkg_metadata(_):
        pm = ToolPackageManager()
        for pkg in pm.get_installed():
            if not pkg.metadata or pkg.metadata.spec.external or pkg.metadata.spec.id:
                continue
            result = pm.search_registry_packages(PackageSpec(name=pkg.metadata.name))
            if len(result) != 1:
                continue
            result = result[0]
            pkg.metadata.spec = PackageSpec(
                id=result["id"],
                owner=result["owner"]["username"],
                name=result["name"],
            )
            pkg.dump_meta()
        return True


def after_upgrade(ctx):
    terminal_width, _ = shutil.get_terminal_size()
    last_version = app.get_state_item("last_version", "0.0.0")
    if last_version == __version__:
        return

    if last_version == "0.0.0":
        app.set_state_item("last_version", __version__)
    elif pepver_to_semver(last_version) > pepver_to_semver(__version__):
        click.secho("*" * terminal_width, fg="yellow")
        click.secho(
            "Obsolete PIO Core v%s is used (previous was %s)"
            % (__version__, last_version),
            fg="yellow",
        )
        click.secho("Please remove multiple PIO Cores from a system:", fg="yellow")
        click.secho(
            "https://docs.platformio.org/page/faq.html"
            "#multiple-platformio-cores-in-a-system",
            fg="cyan",
        )
        click.secho("*" * terminal_width, fg="yellow")
        return
    else:
        click.secho("Please wait while upgrading PlatformIO...", fg="yellow")
        try:
            cleanup_content_cache("http")
        except:  # pylint: disable=bare-except
            pass

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
    if not os.getenv("PLATFORMIO_IDE"):
        click.echo(
            "- %s PlatformIO IDE for embedded development > %s"
            % (
                click.style("try", fg="cyan"),
                click.style("https://platformio.org/platformio-ide", fg="cyan"),
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

    http.ensure_internet_on(raise_exception=True)

    # Update PlatformIO's Core packages
    update_core_packages(silent=True)

    latest_version = get_latest_version()
    if pepver_to_semver(latest_version) <= pepver_to_semver(__version__):
        return

    terminal_width, _ = shutil.get_terminal_size()

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho(
        "There is a new version %s of PlatformIO available.\n"
        "Please upgrade it via `" % latest_version,
        fg="yellow",
        nl=False,
    )
    if os.getenv("PLATFORMIO_IDE"):
        click.secho("PlatformIO IDE Menu: Upgrade PlatformIO", fg="cyan", nl=False)
        click.secho("`.", fg="yellow")
    elif os.path.join("Cellar", "platformio") in fs.get_source_dir():
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


def check_internal_updates(ctx, what):  # pylint: disable=too-many-branches
    last_check = app.get_state_item("last_check", {})
    interval = int(app.get_setting("check_%s_interval" % what)) * 3600 * 24
    if (time() - interval) < last_check.get(what + "_update", 0):
        return

    last_check[what + "_update"] = int(time())
    app.set_state_item("last_check", last_check)

    http.ensure_internet_on(raise_exception=True)

    outdated_items = []
    pm = PlatformPackageManager() if what == "platforms" else LibraryPackageManager()
    for pkg in pm.get_installed():
        if pkg.metadata.name in outdated_items:
            continue
        conds = [
            pm.outdated(pkg).is_outdated(),
            what == "platforms" and PlatformFactory.new(pkg).are_outdated_packages(),
        ]
        if any(conds):
            outdated_items.append(pkg.metadata.name)

    if not outdated_items:
        return

    terminal_width, _ = shutil.get_terminal_size()

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


def check_prune_system():
    last_check = app.get_state_item("last_check", {})
    interval = 30 * 3600 * 24  # 1 time per month
    if (time() - interval) < last_check.get("prune_system", 0):
        return

    last_check["prune_system"] = int(time())
    app.set_state_item("last_check", last_check)
    threshold_mb = int(app.get_setting("check_prune_system_threshold") or 0)
    if threshold_mb <= 0:
        return

    unnecessary_size = calculate_unnecessary_system_data()
    if (unnecessary_size / 1024) < threshold_mb:
        return

    terminal_width, _ = shutil.get_terminal_size()
    click.echo()
    click.echo("*" * terminal_width)
    click.secho(
        "We found %s of unnecessary PlatformIO system data (temporary files, "
        "unnecessary packages, etc.).\nUse `pio system prune --dry-run` to list "
        "them or `pio system prune` to save disk space."
        % fs.humanize_file_size(unnecessary_size),
        fg="yellow",
    )
