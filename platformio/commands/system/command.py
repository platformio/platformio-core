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
import platform
import subprocess
import sys

import click
from tabulate import tabulate

from platformio import __version__, compat, proc, util
from platformio.commands.system.completion import (
    get_completion_install_path,
    install_completion_code,
    uninstall_completion_code,
)
from platformio.managers.platform import PlatformManager
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.project.config import ProjectConfig


@click.group("system", short_help="Miscellaneous system commands")
def cli():
    pass


@cli.command("info", short_help="Display system-wide information")
@click.option("--json-output", is_flag=True)
def system_info(json_output):
    project_config = ProjectConfig()
    data = {}
    data["core_version"] = {"title": "PlatformIO Core", "value": __version__}
    data["python_version"] = {
        "title": "Python",
        "value": "{0}.{1}.{2}-{3}.{4}".format(*list(sys.version_info)),
    }
    data["system"] = {"title": "System Type", "value": util.get_systype()}
    data["platform"] = {"title": "Platform", "value": platform.platform(terse=True)}
    data["filesystem_encoding"] = {
        "title": "File System Encoding",
        "value": compat.get_filesystem_encoding(),
    }
    data["locale_encoding"] = {
        "title": "Locale Encoding",
        "value": compat.get_locale_encoding(),
    }
    data["core_dir"] = {
        "title": "PlatformIO Core Directory",
        "value": project_config.get_optional_dir("core"),
    }
    data["platformio_exe"] = {
        "title": "PlatformIO Core Executable",
        "value": proc.where_is_program(
            "platformio.exe" if proc.WINDOWS else "platformio"
        ),
    }
    data["python_exe"] = {
        "title": "Python Executable",
        "value": proc.get_pythonexe_path(),
    }
    data["global_lib_nums"] = {
        "title": "Global Libraries",
        "value": len(LibraryPackageManager().get_installed()),
    }
    data["dev_platform_nums"] = {
        "title": "Development Platforms",
        "value": len(PlatformManager().get_installed()),
    }
    data["package_tool_nums"] = {
        "title": "Tools & Toolchains",
        "value": len(
            ToolPackageManager(
                project_config.get_optional_dir("packages")
            ).get_installed()
        ),
    }

    click.echo(
        json.dumps(data)
        if json_output
        else tabulate([(item["title"], item["value"]) for item in data.values()])
    )


@cli.group("completion", short_help="Shell completion support")
def completion():
    # pylint: disable=import-error,import-outside-toplevel
    try:
        import click_completion  # pylint: disable=unused-import,unused-variable
    except ImportError:
        click.echo("Installing dependent packages...")
        subprocess.check_call(
            [proc.get_pythonexe_path(), "-m", "pip", "install", "click-completion"],
        )


@completion.command("install", short_help="Install shell completion files/code")
@click.option(
    "--shell",
    default=None,
    type=click.Choice(["fish", "bash", "zsh", "powershell", "auto"]),
    help="The shell type, default=auto",
)
@click.option(
    "--path",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    help="Custom installation path of the code to be evaluated by the shell. "
    "The standard installation path is used by default.",
)
def completion_install(shell, path):

    import click_completion  # pylint: disable=import-outside-toplevel,import-error

    shell = shell or click_completion.get_auto_shell()
    path = path or get_completion_install_path(shell)
    install_completion_code(shell, path)
    click.echo(
        "PlatformIO CLI completion has been installed for %s shell to %s \n"
        "Please restart a current shell session."
        % (click.style(shell, fg="cyan"), click.style(path, fg="blue"))
    )


@completion.command("uninstall", short_help="Uninstall shell completion files/code")
@click.option(
    "--shell",
    default=None,
    type=click.Choice(["fish", "bash", "zsh", "powershell", "auto"]),
    help="The shell type, default=auto",
)
@click.option(
    "--path",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    help="Custom installation path of the code to be evaluated by the shell. "
    "The standard installation path is used by default.",
)
def completion_uninstall(shell, path):

    import click_completion  # pylint: disable=import-outside-toplevel,import-error

    shell = shell or click_completion.get_auto_shell()
    path = path or get_completion_install_path(shell)
    uninstall_completion_code(shell, path)
    click.echo(
        "PlatformIO CLI completion has been uninstalled for %s shell from %s \n"
        "Please restart a current shell session."
        % (click.style(shell, fg="cyan"), click.style(path, fg="blue"))
    )
