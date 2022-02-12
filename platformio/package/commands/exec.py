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

from platformio.compat import IS_MACOS, IS_WINDOWS
from platformio.exception import UserSideException
from platformio.package.manager.tool import ToolPackageManager
from platformio.proc import get_pythonexe_path


@click.command("exec", short_help="Run command from package tool")
@click.option("-p", "--package", metavar="<pkg>[@<version>]")
@click.option("-c", "--call", metavar="<cmd> [args...]")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def package_exec_cmd(package, call, args):
    if not call and not args:
        raise click.BadArgumentUsage("Please provide command name")
    pkg = None
    if package:
        pm = ToolPackageManager()
        pkg = pm.get_package(package)
        if not pkg:
            pkg = pm.install(package)
    else:
        executable = args[0] if args else call.split(" ")[0]
        pkg = find_pkg_by_executable(executable)
        if not pkg:
            raise UserSideException(
                "Could not find a package with '%s' executable file" % executable
            )

    click.echo(
        "Using %s package"
        % click.style("%s@%s" % (pkg.metadata.name, pkg.metadata.version), fg="green")
    )

    inject_pkg_to_environ(pkg)
    os.environ["PIO_PYTHON_EXE"] = get_pythonexe_path()
    try:
        subprocess.run(  # pylint: disable=subprocess-run-check
            call or args, shell=call is not None, env=os.environ
        )
    except Exception as exc:
        raise UserSideException(exc)


def find_pkg_by_executable(executable):
    exes = [executable]
    if IS_WINDOWS and not executable.endswith(".exe"):
        exes.append(f"{executable}.exe")
    for pkg in ToolPackageManager().get_installed():
        for exe in exes:
            if os.path.exists(os.path.join(pkg.path, exe)) or os.path.exists(
                os.path.join(pkg.path, "bin", exe)
            ):
                return pkg
    return None


def inject_pkg_to_environ(pkg):
    bin_dir = os.path.join(pkg.path, "bin")
    lib_dir = os.path.join(pkg.path, "lib")

    paths = [bin_dir, pkg.path] if os.path.isdir(bin_dir) else [pkg.path]
    if os.environ.get("PATH"):
        paths.append(os.environ.get("PATH"))
    os.environ["PATH"] = os.pathsep.join(paths)

    if IS_WINDOWS or not os.path.isdir(lib_dir) or "toolchain" in pkg.metadata.name:
        return

    lib_path_key = "DYLD_LIBRARY_PATH" if IS_MACOS else "LD_LIBRARY_PATH"
    lib_paths = [lib_dir]
    if os.environ.get(lib_path_key):
        lib_paths.append(os.environ.get(lib_path_key))
    os.environ[lib_path_key] = os.pathsep.join(lib_paths)
