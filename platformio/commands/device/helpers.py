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

import inspect
import os

from serial.tools import miniterm

from platformio import fs
from platformio.commands.device import DeviceMonitorFilter
from platformio.compat import get_object_members, load_python_module
from platformio.project.config import ProjectConfig


def apply_project_monitor_options(cli_options, project_options):
    for k in ("port", "speed", "rts", "dtr"):
        k2 = "monitor_%s" % k
        if k == "speed":
            k = "baud"
        if cli_options[k] is None and k2 in project_options:
            cli_options[k] = project_options[k2]
            if k != "port":
                cli_options[k] = int(cli_options[k])
    return cli_options


def options_to_argv(cli_options, project_options, ignore=None):
    confmon_flags = project_options.get("monitor_flags", [])
    result = confmon_flags[::]

    for f in project_options.get("monitor_filters", []):
        result.extend(["--filter", f])

    for k, v in cli_options.items():
        if v is None or (ignore and k in ignore):
            continue
        k = "--" + k.replace("_", "-")
        if k in confmon_flags:
            continue
        if isinstance(v, bool):
            if v:
                result.append(k)
        elif isinstance(v, tuple):
            for i in v:
                result.extend([k, i])
        else:
            result.extend([k, str(v)])
    return result


def get_project_options(environment=None):
    config = ProjectConfig.get_instance()
    config.validate(envs=[environment] if environment else None)
    if not environment:
        default_envs = config.default_envs()
        if default_envs:
            environment = default_envs[0]
        else:
            environment = config.envs()[0]
    return config.items(env=environment, as_dict=True)


def get_board_hwids(project_dir, platform, board):
    with fs.cd(project_dir):
        return platform.board_config(board).get("build.hwids", [])


def load_monitor_filter(path, project_dir=None, environment=None):
    name = os.path.basename(path)
    name = name[: name.find(".")]
    module = load_python_module("platformio.commands.device.filters.%s" % name, path)
    for cls in get_object_members(module).values():
        if (
            not inspect.isclass(cls)
            or not issubclass(cls, DeviceMonitorFilter)
            or cls == DeviceMonitorFilter
        ):
            continue
        obj = cls(project_dir, environment)
        miniterm.TRANSFORMATIONS[obj.NAME] = obj
    return True


def register_platform_filters(platform, project_dir, environment):
    monitor_dir = os.path.join(platform.get_dir(), "monitor")
    if not os.path.isdir(monitor_dir):
        return

    for name in os.listdir(monitor_dir):
        if not name.startswith("filter_") or not name.endswith(".py"):
            continue
        path = os.path.join(monitor_dir, name)
        if not os.path.isfile(path):
            continue
        load_monitor_filter(path, project_dir, environment)
