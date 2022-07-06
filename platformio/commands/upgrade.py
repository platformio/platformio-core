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

import json
import os
import re
from zipfile import ZipFile

import click

from platformio import VERSION, __version__, app, exception
from platformio.compat import IS_WINDOWS
from platformio.http import fetch_remote_content
from platformio.package.manager.core import update_core_packages
from platformio.proc import exec_command, get_pythonexe_path
from platformio.project.helpers import get_project_cache_dir


@click.command("upgrade", short_help="Upgrade PlatformIO Core to the latest version")
@click.option("--dev", is_flag=True, help="Use development branch")
def cli(dev):
    update_core_packages()
    if not dev and __version__ == get_latest_version():
        return click.secho(
            "You're up-to-date!\nPlatformIO %s is currently the "
            "newest version available." % __version__,
            fg="green",
        )

    click.secho("Please wait while upgrading PlatformIO ...", fg="yellow")

    to_develop = dev or not all(c.isdigit() for c in __version__ if c != ".")
    cmds = (
        ["pip", "install", "--upgrade", download_dist_package(to_develop)],
        ["platformio", "--version"],
    )

    cmd = None
    r = {}
    try:
        for cmd in cmds:
            cmd = [get_pythonexe_path(), "-m"] + cmd
            r = exec_command(cmd)

            # try pip with disabled cache
            if r["returncode"] != 0 and cmd[2] == "pip":
                cmd.insert(3, "--no-cache-dir")
                r = exec_command(cmd)

            assert r["returncode"] == 0
        assert "version" in r["out"]
        actual_version = r["out"].strip().split("version", 1)[1].strip()
        click.secho(
            "PlatformIO has been successfully upgraded to %s" % actual_version,
            fg="green",
        )
        click.echo("Release notes: ", nl=False)
        click.secho("https://docs.platformio.org/en/latest/history.html", fg="cyan")
        if app.get_session_var("caller_id"):
            click.secho(
                "Warning! Please restart IDE to affect PIO Home changes", fg="yellow"
            )
    except Exception as exc:
        if not r:
            raise exception.UpgradeError("\n".join([str(cmd), str(exc)])) from exc
        permission_errors = ("permission denied", "not permitted")
        if any(m in r["err"].lower() for m in permission_errors) and not IS_WINDOWS:
            click.secho(
                """
-----------------
Permission denied
-----------------
You need the `sudo` permission to install Python packages. Try

> sudo pip install -U platformio

WARNING! Don't use `sudo` for the rest PlatformIO commands.
""",
                fg="yellow",
                err=True,
            )
            raise exception.ReturnErrorCode(1)
        raise exception.UpgradeError("\n".join([str(cmd), r["out"], r["err"]]))

    return True


def download_dist_package(to_develop):
    if not to_develop:
        return "platformio"
    dl_url = "https://github.com/platformio/platformio-core/archive/develop.zip"
    cache_dir = get_project_cache_dir()
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    pkg_name = os.path.join(cache_dir, "piocoredevelop.zip")
    try:
        with open(pkg_name, "wb") as fp:
            r = exec_command(
                ["curl", "-fsSL", dl_url], stdout=fp, universal_newlines=True
            )
            assert r["returncode"] == 0
        # check ZIP structure
        with ZipFile(pkg_name) as zp:
            assert zp.testzip() is None
        return pkg_name
    except:  # pylint: disable=bare-except
        pass
    return dl_url


def get_latest_version():
    try:
        if not str(VERSION[2]).isdigit():
            try:
                return get_develop_latest_version()
            except:  # pylint: disable=bare-except
                pass
        return get_pypi_latest_version()
    except Exception as exc:
        raise exception.GetLatestVersionError() from exc


def get_develop_latest_version():
    version = None
    content = fetch_remote_content(
        "https://raw.githubusercontent.com/platformio/platformio"
        "/develop/platformio/__init__.py"
    )
    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("VERSION"):
            continue
        match = re.match(r"VERSION\s*=\s*\(([^\)]+)\)", line)
        if not match:
            continue
        version = match.group(1)
        for c in (" ", "'", '"'):
            version = version.replace(c, "")
        version = ".".join(version.split(","))
    assert version
    return version


def get_pypi_latest_version():
    content = fetch_remote_content("https://pypi.org/pypi/platformio/json")
    return json.loads(content)["info"]["version"]
