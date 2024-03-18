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
import re
import subprocess

import click

from platformio import VERSION, __version__, app, exception
from platformio.dependencies import get_pip_dependencies
from platformio.http import fetch_remote_content
from platformio.package.manager.core import update_core_packages
from platformio.proc import get_pythonexe_path

PYPI_JSON_URL = "https://pypi.org/pypi/platformio/json"
DEVELOP_ZIP_URL = "https://github.com/platformio/platformio-core/archive/develop.zip"
DEVELOP_INIT_SCRIPT_URL = (
    "https://raw.githubusercontent.com/platformio/platformio-core"
    "/develop/platformio/__init__.py"
)


@click.command("upgrade", short_help="Upgrade PlatformIO Core to the latest version")
@click.option("--dev", is_flag=True, help="Use development branch")
@click.option("--only-dependencies", is_flag=True)
@click.option("--verbose", "-v", is_flag=True)
def cli(dev, only_dependencies, verbose):
    if only_dependencies:
        return upgrade_pip_dependencies(verbose)

    update_core_packages()

    if not dev and __version__ == get_latest_version():
        return click.secho(
            "You're up-to-date!\nPlatformIO %s is currently the "
            "newest version available." % __version__,
            fg="green",
        )

    click.secho("Please wait while upgrading PlatformIO Core ...", fg="yellow")

    python_exe = get_pythonexe_path()
    to_develop = dev or not all(c.isdigit() for c in __version__ if c != ".")
    pkg_spec = DEVELOP_ZIP_URL if to_develop else "platformio"

    try:
        # PIO Core
        subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", pkg_spec],
            check=True,
            stdout=subprocess.PIPE if not verbose else None,
        )

        # PyPI dependencies
        subprocess.run(
            [python_exe, "-m", "platformio", "upgrade", "--only-dependencies"],
            check=False,
            stdout=subprocess.PIPE,
        )

        # Check version
        output = subprocess.run(
            [python_exe, "-m", "platformio", "--version"],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode()
        assert "version" in output
        actual_version = output.split("version", 1)[1].strip()
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
    except (AssertionError, subprocess.CalledProcessError) as exc:
        click.secho(
            "\nWarning!!! Could not automatically upgrade the PlatformIO Core.",
            fg="red",
        )
        click.secho(
            "Please upgrade it manually using the following command:\n",
            fg="red",
        )
        click.secho(f'"{python_exe}" -m pip install -U {pkg_spec}\n', fg="cyan")
        raise exception.ReturnErrorCode(1) from exc

    return True


def upgrade_pip_dependencies(verbose):
    subprocess.run(
        [
            get_pythonexe_path(),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            *get_pip_dependencies(),
        ],
        check=True,
        stdout=subprocess.PIPE if not verbose else None,
    )


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
    content = fetch_remote_content(DEVELOP_INIT_SCRIPT_URL)
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
    content = fetch_remote_content(PYPI_JSON_URL)
    return json.loads(content)["info"]["version"]
