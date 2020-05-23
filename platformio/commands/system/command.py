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


import subprocess

import click

from platformio import proc
from platformio.commands.system.completion import (
    get_completion_install_path,
    install_completion_code,
    uninstall_completion_code,
)


@click.group("system", short_help="Miscellaneous system commands")
def cli():
    pass


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
