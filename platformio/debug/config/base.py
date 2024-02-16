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
import os

from platformio import fs, proc, util
from platformio.compat import string_types
from platformio.debug.exception import DebugInvalidOptionsError
from platformio.project.config import ProjectConfig
from platformio.project.helpers import load_build_metadata
from platformio.project.options import ProjectOptions


class DebugConfigBase:  # pylint: disable=too-many-instance-attributes
    DEFAULT_PORT = None

    def __init__(self, platform, project_config, env_name):
        self.platform = platform
        self.project_config = project_config
        self.env_name = env_name
        self.env_options = project_config.items(env=env_name, as_dict=True)
        self.build_data = self._load_build_data()

        self.tool_name = None
        self.board_config = {}
        self.tool_settings = {}
        if "board" in self.env_options:
            self.board_config = platform.board_config(self.env_options["board"])
            self.tool_name = self.board_config.get_debug_tool_name(
                self.env_options.get("debug_tool")
            )
            self.tool_settings = (
                self.board_config.get("debug", {})
                .get("tools", {})
                .get(self.tool_name, {})
            )

        self._load_cmds = None
        self._port = None

        self.server = self._configure_server()

        try:
            platform.configure_debug_session(self)
        except NotImplementedError:
            pass

    @staticmethod
    def cleanup_cmds(items):
        items = ProjectConfig.parse_multi_values(items)
        return ["$LOAD_CMDS" if item == "$LOAD_CMD" else item for item in items]

    @property
    def program_path(self):
        return self.build_data["prog_path"]

    @property
    def client_executable_path(self):
        return self.build_data["gdb_path"]

    @property
    def load_cmds(self):
        if self._load_cmds is not None:
            return self._load_cmds
        result = self.env_options.get("debug_load_cmds")
        if not result:
            result = self.tool_settings.get("load_cmds")
        if not result:
            # legacy
            result = self.tool_settings.get("load_cmd")
        if not result:
            result = ProjectOptions["env.debug_load_cmds"].default
        return self.cleanup_cmds(result)

    @load_cmds.setter
    def load_cmds(self, cmds):
        self._load_cmds = cmds

    @property
    def load_mode(self):
        result = self.env_options.get("debug_load_mode")
        if not result:
            result = self.tool_settings.get("load_mode")
        return result or ProjectOptions["env.debug_load_mode"].default

    @property
    def init_break(self):
        missed = object()
        result = self.env_options.get("debug_init_break", missed)
        if result != missed:
            return result
        result = None
        if not result:
            result = self.tool_settings.get("init_break")
        return result or ProjectOptions["env.debug_init_break"].default

    @property
    def init_cmds(self):
        return self.cleanup_cmds(
            self.env_options.get("debug_init_cmds", self.tool_settings.get("init_cmds"))
        )

    @property
    def extra_cmds(self):
        return self.cleanup_cmds(
            self.env_options.get("debug_extra_cmds")
        ) + self.cleanup_cmds(self.tool_settings.get("extra_cmds"))

    @property
    def port(self):
        return (
            self._port
            or self.env_options.get("debug_port")
            or self.tool_settings.get("port")
            or self.DEFAULT_PORT
        )

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def upload_protocol(self):
        return self.env_options.get(
            "upload_protocol", self.board_config.get("upload", {}).get("protocol")
        )

    @property
    def speed(self):
        return self.env_options.get("debug_speed", self.tool_settings.get("speed"))

    @property
    def server_ready_pattern(self):
        return self.env_options.get(
            "debug_server_ready_pattern", (self.server or {}).get("ready_pattern")
        )

    def _load_build_data(self):
        data = load_build_metadata(
            os.getcwd(), self.env_name, cache=True, build_type="debug"
        )
        if not data:
            raise DebugInvalidOptionsError("Could not load a build configuration")
        return data

    def _configure_server(self):
        # user disabled server in platformio.ini
        if "debug_server" in self.env_options and not self.env_options.get(
            "debug_server"
        ):
            return None

        result = None

        # specific server per a system
        if isinstance(self.tool_settings.get("server", {}), list):
            for item in self.tool_settings["server"][:]:
                self.tool_settings["server"] = item
                if util.get_systype() in item.get("system", []):
                    break

        # user overwrites debug server
        if self.env_options.get("debug_server"):
            result = {
                "cwd": None,
                "executable": None,
                "arguments": self.env_options.get("debug_server"),
            }
            result["executable"] = result["arguments"][0]
            result["arguments"] = result["arguments"][1:]
        elif "server" in self.tool_settings:
            result = self.tool_settings["server"]
            server_package = result.get("package")
            server_package_dir = (
                self.platform.get_package_dir(server_package)
                if server_package
                else None
            )
            if server_package and not server_package_dir:
                self.platform.install_package(server_package)
                server_package_dir = self.platform.get_package_dir(server_package)
            result.update(
                dict(
                    cwd=server_package_dir if server_package else None,
                    executable=result.get("executable"),
                    arguments=[
                        (
                            a.replace("$PACKAGE_DIR", server_package_dir)
                            if server_package_dir
                            else a
                        )
                        for a in result.get("arguments", [])
                    ],
                )
            )
        return self.reveal_patterns(result) if result else None

    def get_init_script(self, debugger):
        try:
            return getattr(self, "%s_INIT_SCRIPT" % debugger.upper())
        except AttributeError as exc:
            raise NotImplementedError from exc

    def reveal_patterns(self, source, recursive=True):
        program_path = self.program_path or ""
        patterns = {
            "PLATFORMIO_CORE_DIR": self.project_config.get("platformio", "core_dir"),
            "PYTHONEXE": proc.get_pythonexe_path(),
            "PROJECT_DIR": os.getcwd(),
            "PROG_PATH": program_path,
            "PROG_DIR": os.path.dirname(program_path),
            "PROG_NAME": os.path.basename(os.path.splitext(program_path)[0]),
            "DEBUG_PORT": self.port,
            "UPLOAD_PROTOCOL": self.upload_protocol,
            "INIT_BREAK": self.init_break or "",
            "LOAD_CMDS": "\n".join(self.load_cmds or []),
        }
        for key, value in patterns.items():
            if key.endswith(("_DIR", "_PATH")):
                patterns[key] = fs.to_unix_path(value)

        def _replace(text):
            for key, value in patterns.items():
                pattern = "$%s" % key
                text = text.replace(pattern, value or "")
            return text

        if isinstance(source, string_types):
            source = _replace(source)
        elif isinstance(source, (list, dict)):
            items = enumerate(source) if isinstance(source, list) else source.items()
            for key, value in items:
                if isinstance(value, string_types):
                    source[key] = _replace(value)
                elif isinstance(value, (list, dict)) and recursive:
                    source[key] = self.reveal_patterns(value, patterns)

        data = json.dumps(source)
        if any(("$" + key) in data for key in patterns):
            source = self.reveal_patterns(source, patterns)

        return source
