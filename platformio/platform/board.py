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

from platformio import fs, telemetry, util
from platformio.compat import MISSING
from platformio.debug.exception import DebugInvalidOptionsError, DebugSupportError
from platformio.exception import UserSideException
from platformio.platform.exception import InvalidBoardManifest


class PlatformBoardConfig:
    def __init__(self, manifest_path):
        self._id = os.path.basename(manifest_path)[:-5]
        assert os.path.isfile(manifest_path)
        self.manifest_path = manifest_path
        try:
            self._manifest = fs.load_json(manifest_path)
        except ValueError as exc:
            raise InvalidBoardManifest(manifest_path) from exc
        if not set(["name", "url", "vendor"]) <= set(self._manifest):
            raise UserSideException(
                "Please specify name, url and vendor fields for " + manifest_path
            )

    def get(self, path, default=MISSING):
        try:
            value = self._manifest
            for k in path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default != MISSING:
                return default
        raise KeyError("Invalid board option '%s'" % path)

    def update(self, path, value):
        newdict = None
        for key in path.split(".")[::-1]:
            if newdict is None:
                newdict = {key: value}
            else:
                newdict = {key: newdict}
        util.merge_dicts(self._manifest, newdict)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    @property
    def id(self):
        return self._id

    @property
    def id_(self):
        return self.id

    @property
    def manifest(self):
        return self._manifest

    def get_brief_data(self):
        result = {
            "id": self.id,
            "name": self._manifest["name"],
            "platform": self._manifest.get("platform"),
            "mcu": self._manifest.get("build", {}).get("mcu", "").upper(),
            "fcpu": int(
                "".join(
                    [
                        c
                        for c in str(self._manifest.get("build", {}).get("f_cpu", "0L"))
                        if c.isdigit()
                    ]
                )
            ),
            "ram": self._manifest.get("upload", {}).get("maximum_ram_size", 0),
            "rom": self._manifest.get("upload", {}).get("maximum_size", 0),
            "frameworks": self._manifest.get("frameworks"),
            "vendor": self._manifest["vendor"],
            "url": self._manifest["url"],
        }
        if self._manifest.get("connectivity"):
            result["connectivity"] = self._manifest.get("connectivity")
        debug = self.get_debug_data()
        if debug:
            result["debug"] = debug
        return result

    def get_debug_data(self):
        if not self._manifest.get("debug", {}).get("tools"):
            return None
        tools = {}
        for name, options in self._manifest["debug"]["tools"].items():
            tools[name] = {}
            for key, value in options.items():
                if key in ("default", "onboard") and value:
                    tools[name][key] = value
        return {"tools": tools}

    def get_debug_tool_name(self, custom=None):
        debug_tools = self._manifest.get("debug", {}).get("tools")
        tool_name = custom
        if tool_name == "custom":
            return tool_name
        if not debug_tools:
            telemetry.send_event("Debug", "Request", self.id)
            raise DebugSupportError(self._manifest["name"])
        if tool_name:
            if tool_name in debug_tools:
                return tool_name
            raise DebugInvalidOptionsError(
                "Unknown debug tool `%s`. Please use one of `%s` or `custom`"
                % (tool_name, ", ".join(sorted(list(debug_tools))))
            )

        # automatically select best tool
        data = {"default": [], "onboard": [], "external": []}
        for key, value in debug_tools.items():
            if value.get("default"):
                data["default"].append(key)
            elif value.get("onboard"):
                data["onboard"].append(key)
            data["external"].append(key)

        for key, value in data.items():
            if not value:
                continue
            return sorted(value)[0]

        assert any(item for item in data)
