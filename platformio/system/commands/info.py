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
import sys

import click
from tabulate import tabulate

from platformio import __version__, compat, proc, util
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.project.config import ProjectConfig


@click.command("info", short_help="Display system-wide information")
@click.option("--json-output", is_flag=True)
def system_info_cmd(json_output):
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
        "value": project_config.get("platformio", "core_dir"),
    }
    data["platformio_exe"] = {
        "title": "PlatformIO Core Executable",
        "value": proc.where_is_program(
            "platformio.exe" if compat.IS_WINDOWS else "platformio"
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
        "value": len(PlatformPackageManager().get_installed()),
    }
    data["package_tool_nums"] = {
        "title": "Tools & Toolchains",
        "value": len(
            ToolPackageManager(
                project_config.get("platformio", "packages_dir")
            ).get_installed()
        ),
    }

    click.echo(
        json.dumps(data)
        if json_output
        else tabulate([(item["title"], item["value"]) for item in data.values()])
    )
