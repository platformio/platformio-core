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

from serial.tools import miniterm

from platformio.project.config import ProjectConfig


class DeviceMonitorFilter(miniterm.Transform):
    def __init__(self, project_dir=None, environment=None):
        """ Called by PlatformIO to pass context """
        miniterm.Transform.__init__(self)

        self.project_dir = project_dir
        self.environment = environment

        self.config = ProjectConfig.get_instance()
        if not self.environment:
            default_envs = self.config.default_envs()
            if default_envs:
                self.environment = default_envs[0]
            elif self.config.envs():
                self.environment = self.config.envs()[0]

    def __call__(self):
        """ Called by the miniterm library when the filter is actually used """
        return self

    @property
    def NAME(self):
        raise NotImplementedError("Please declare NAME attribute for the filter class")
