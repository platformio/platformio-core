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

import importlib
import re

from platformio.debug.config.generic import GenericDebugConfig
from platformio.debug.config.native import NativeDebugConfig


class DebugConfigFactory:
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_\-]+", "", name, flags=re.I)
        return "%sDebugConfig" % name.lower().capitalize()

    @classmethod
    def new(cls, platform, project_config, env_name):
        board_config = platform.board_config(
            project_config.get("env:" + env_name, "board")
        )
        tool_name = (
            board_config.get_debug_tool_name(
                project_config.get("env:" + env_name, "debug_tool")
            )
            if board_config
            else None
        )
        config_cls = None
        try:
            mod = importlib.import_module("platformio.debug.config.%s" % tool_name)
            config_cls = getattr(mod, cls.get_clsname(tool_name))
        except ModuleNotFoundError:
            config_cls = (
                GenericDebugConfig if platform.is_embedded() else NativeDebugConfig
            )
        return config_cls(platform, project_config, env_name)
