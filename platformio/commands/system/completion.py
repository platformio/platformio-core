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
import subprocess

import click


def get_completion_install_path(shell):
    home_dir = os.path.expanduser("~")
    prog_name = click.get_current_context().find_root().info_name
    if shell == "fish":
        return os.path.join(
            home_dir, ".config", "fish", "completions", "%s.fish" % prog_name
        )
    if shell == "bash":
        return os.path.join(home_dir, ".bash_completion")
    if shell == "zsh":
        return os.path.join(home_dir, ".zshrc")
    if shell == "powershell":
        return subprocess.check_output(
            ["powershell", "-NoProfile", "echo $profile"]
        ).strip()
    raise click.ClickException("%s is not supported." % shell)


def is_completion_code_installed(shell, path):
    if shell == "fish" or not os.path.exists(path):
        return False

    import click_completion  # pylint: disable=import-error,import-outside-toplevel

    with open(path, encoding="utf8") as fp:
        return click_completion.get_code(shell=shell) in fp.read()


def install_completion_code(shell, path):
    import click_completion  # pylint: disable=import-error,import-outside-toplevel

    if is_completion_code_installed(shell, path):
        return None

    return click_completion.install(shell=shell, path=path, append=shell != "fish")


def uninstall_completion_code(shell, path):
    if not os.path.exists(path):
        return True
    if shell == "fish":
        os.remove(path)
        return True

    import click_completion  # pylint: disable=import-error,import-outside-toplevel

    with open(path, "r+", encoding="utf8") as fp:
        contents = fp.read()
        fp.seek(0)
        fp.truncate()
        fp.write(contents.replace(click_completion.get_code(shell=shell), ""))

    return True
