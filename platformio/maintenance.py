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
from platformio.cli import PlatformioCLI
from platformio.commands.upgrade import get_latest_version
from platformio.http import HTTPClientError, InternetConnectionError, ensure_internet_on
from platformio.package.manager.core import update_core_packages
from platformio.package.version import pepver_to_semver
from platformio.system.prune import calculate_unnecessary_system_data


def on_cmd_start(ctx, caller):
    app.set_session_var("command_ctx", ctx)
    set_caller(caller)
    telemetry.on_cmd_start(ctx)
    if PlatformioCLI.in_silence():
        return
    after_upgrade(ctx)


def on_cmd_end():
    if PlatformioCLI.in_silence():
        return

    try:
        check_platformio_upgrade()
        check_prune_system()
    except (
        HTTPClientError,
        InternetConnectionError,
        exception.GetLatestVersionError,
    ):
        click.secho(
            "Failed to check for PlatformIO upgrades. "
            "Please check your Internet connection.",
            fg="red",
        )


def on_platformio_exception(exc):
    telemetry.log_exception(exc)


def on_platformio_exit():
    telemetry.on_exit()


def set_caller(caller=None):
    caller = caller or os.getenv("PLATFORMIO_CALLER")
    if not caller:
        if os.getenv("CODESPACES"):
            caller = "codespaces"
        elif os.getenv("VSCODE_PID") or os.getenv("VSCODE_NLS_CONFIG"):
            caller = "vscode"
        elif os.getenv("GITPOD_WORKSPACE_ID") or os.getenv("GITPOD_WORKSPACE_URL"):
            caller = "gitpod"
    if caller:
        app.set_session_var("caller_id", caller)


class Upgrader:
    def __init__(self, from_version, to_version):
        self.from_version = from_version
        self.to_version = to_version
        self._upgraders = [
            (semantic_version.Version("6.1.8-a.1"), self._appstate_migration),
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
    def _appstate_migration(_):
        state_path = app.resolve_state_path("core_dir", "appstate.json")
        if not os.path.isfile(state_path):
            return True
        app.delete_state_item("telemetry")
        created_at = app.get_state_item("created_at", None)
        if not created_at:
            state_stat = os.stat(state_path)
            app.set_state_item(
                "created_at",
                int(
                    state_stat.st_birthtime
                    if hasattr(state_stat, "st_birthtime")
                    else state_stat.st_ctime
                ),
            )
        return True


def after_upgrade(ctx):
    terminal_width = shutil.get_terminal_size().columns
    last_version_str = app.get_state_item("last_version", "0.0.0")
    if last_version_str == __version__:
        return None

    if last_version_str == "0.0.0":
        app.set_state_item("last_version", __version__)
        return print_welcome_banner()

    last_version = pepver_to_semver(last_version_str)
    current_version = pepver_to_semver(__version__)

    if last_version > current_version and not last_version.prerelease:
        click.secho("*" * terminal_width, fg="yellow")
        click.secho(
            "Obsolete PIO Core v%s is used (previous was %s)"
            % (__version__, last_version_str),
            fg="yellow",
        )
        click.secho("Please remove multiple PIO Cores from a system:", fg="yellow")
        click.secho(
            "https://docs.platformio.org/en/latest/core"
            "/installation/troubleshooting.html",
            fg="cyan",
        )
        click.secho("*" * terminal_width, fg="yellow")
        return None

    click.secho("Please wait while upgrading PlatformIO...", fg="yellow")

    # Update PlatformIO's Core packages
    cleanup_content_cache("http")
    update_core_packages()

    u = Upgrader(last_version, current_version)
    if u.run(ctx):
        app.set_state_item("last_version", __version__)
        click.secho(
            "PlatformIO has been successfully upgraded to %s!\n" % __version__,
            fg="green",
        )
        telemetry.log_event(
            "pio_upgrade_core",
            {
                "label": "%s > %s" % (last_version_str, __version__),
                "from_version": last_version_str,
                "to_version": __version__,
            },
        )

    return print_welcome_banner()


def print_welcome_banner():
    terminal_width = shutil.get_terminal_size().columns
    click.echo("*" * terminal_width)
    click.echo("If you like %s, please:" % (click.style("PlatformIO", fg="cyan")))
    click.echo(
        "- %s it on GitHub > %s"
        % (
            click.style("star", fg="cyan"),
            click.style("https://github.com/platformio/platformio-core", fg="cyan"),
        )
    )
    click.echo(
        "- %s us on LinkedIn to stay up-to-date "
        "on the latest project news > %s"
        % (
            click.style("follow", fg="cyan"),
            click.style("https://www.linkedin.com/company/platformio/", fg="cyan"),
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
    interval = int(app.get_setting("check_platformio_interval")) * 3600 * 24
    check_state = app.get_state_item("last_check", {})
    last_checked_time = check_state.get("platformio_upgrade", 0)
    if (time() - interval) < last_checked_time:
        return

    check_state["platformio_upgrade"] = int(time())
    app.set_state_item("last_check", check_state)
    if not last_checked_time:
        return

    ensure_internet_on(raise_exception=True)

    # Update PlatformIO Core packages
    update_core_packages()

    latest_version = get_latest_version()
    if pepver_to_semver(latest_version) <= pepver_to_semver(__version__):
        return

    terminal_width = shutil.get_terminal_size().columns

    click.echo("")
    click.echo("*" * terminal_width)
    click.secho(
        "There is a new version %s of PlatformIO available.\n"
        "Please upgrade it via `" % latest_version,
        fg="yellow",
        nl=False,
    )
    if os.path.join("Cellar", "platformio") in fs.get_source_dir():
        click.secho("brew update && brew upgrade", fg="cyan", nl=False)
        click.secho("` command.", fg="yellow")
    else:
        click.secho("platformio upgrade", fg="cyan", nl=False)
        click.secho("` or `", fg="yellow", nl=False)
        click.secho("python -m pip install -U platformio", fg="cyan", nl=False)
        click.secho("` command.", fg="yellow")
    click.secho("Changes: ", fg="yellow", nl=False)
    click.secho("https://docs.platformio.org/en/latest/history.html", fg="cyan")
    click.echo("*" * terminal_width)
    click.echo("")


def check_prune_system():
    interval = 30 * 3600 * 24  # 1 time per month
    check_state = app.get_state_item("last_check", {})
    last_checked_time = check_state.get("prune_system", 0)
    if (time() - interval) < last_checked_time:
        return

    check_state["prune_system"] = int(time())
    app.set_state_item("last_check", check_state)

    if not last_checked_time:
        return

    threshold_mb = int(app.get_setting("check_prune_system_threshold") or 0)
    if threshold_mb <= 0:
        return

    unnecessary_size = calculate_unnecessary_system_data()
    if (unnecessary_size / 1024) < threshold_mb:
        return

    terminal_width = shutil.get_terminal_size().columns
    click.echo()
    click.echo("*" * terminal_width)
    click.secho(
        "We found %s of unnecessary PlatformIO system data (temporary files, "
        "unnecessary packages, etc.).\nUse `pio system prune --dry-run` to list "
        "them or `pio system prune` to save disk space."
        % fs.humanize_file_size(unnecessary_size),
        fg="yellow",
    )
