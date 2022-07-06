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

from platformio.compat import get_object_members, load_python_module
from platformio.package.manager.tool import ToolPackageManager
from platformio.project.config import ProjectConfig


class DeviceMonitorFilterBase(miniterm.Transform):
    def __init__(self, options=None):
        """Called by PlatformIO to pass context"""
        miniterm.Transform.__init__(self)

        self.options = options or {}
        self.project_dir = self.options.get("project_dir")
        self.environment = self.options.get("environment")

        self.config = ProjectConfig.get_instance()
        if not self.environment:
            default_envs = self.config.default_envs()
            if default_envs:
                self.environment = default_envs[0]
            elif self.config.envs():
                self.environment = self.config.envs()[0]

    def __call__(self):
        """Called by the miniterm library when the filter is actually used"""
        return self

    @property
    def NAME(self):
        raise NotImplementedError("Please declare NAME attribute for the filter class")


def register_filters(platform=None, options=None):
    # project filters
    load_monitor_filters(
        ProjectConfig.get_instance().get("platformio", "monitor_dir"),
        prefix="filter_",
        options=options,
    )
    # platform filters
    if platform:
        load_monitor_filters(
            os.path.join(platform.get_dir(), "monitor"),
            prefix="filter_",
            options=options,
        )
    # load package filters
    pm = ToolPackageManager()
    for pkg in pm.get_installed():
        load_monitor_filters(
            os.path.join(pkg.path, "monitor"), prefix="filter_", options=options
        )
    # default filters
    load_monitor_filters(os.path.dirname(__file__), options=options)


def load_monitor_filters(monitor_dir, prefix=None, options=None):
    if not os.path.isdir(monitor_dir):
        return
    for name in os.listdir(monitor_dir):
        if (prefix and not name.startswith(prefix)) or not name.endswith(".py"):
            continue
        path = os.path.join(monitor_dir, name)
        if not os.path.isfile(path):
            continue
        load_monitor_filter(path, options)


def load_monitor_filter(path, options=None):
    name = os.path.basename(path)
    name = name[: name.find(".")]
    module = load_python_module("platformio.device.monitor.filters.%s" % name, path)
    for cls in get_object_members(module).values():
        if (
            not inspect.isclass(cls)
            or not issubclass(cls, DeviceMonitorFilterBase)
            or cls == DeviceMonitorFilterBase
        ):
            continue
        obj = cls(options)
        miniterm.TRANSFORMATIONS[obj.NAME] = obj
    return True
