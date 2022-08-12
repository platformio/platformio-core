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
from pathlib import Path

from platformio import __version__, app, fs, util
from platformio.project.config import ProjectConfig
from platformio.project.helpers import is_platformio_project


class AppRPC:

    IGNORE_STORAGE_KEYS = [
        "cid",
        "coreVersion",
        "coreSystype",
        "coreCaller",
        "coreSettings",
        "homeDir",
        "projectsDir",
    ]

    @staticmethod
    def get_state_path():
        core_dir = ProjectConfig.get_instance().get("platformio", "core_dir")
        if not os.path.isdir(core_dir):
            os.makedirs(core_dir)
        return os.path.join(core_dir, "homestate.json")

    @staticmethod
    def load_state():
        with app.State(AppRPC.get_state_path(), lock=True) as state:
            storage = state.get("storage", {})

            # base data
            caller_id = app.get_session_var("caller_id")
            storage["cid"] = app.get_cid()
            storage["coreVersion"] = __version__
            storage["coreSystype"] = util.get_systype()
            storage["coreCaller"] = str(caller_id).lower() if caller_id else None
            storage["coreSettings"] = {
                name: {
                    "description": data["description"],
                    "default_value": data["value"],
                    "value": app.get_setting(name),
                }
                for name, data in app.DEFAULT_SETTINGS.items()
            }

            storage["homeDir"] = fs.expanduser("~")
            storage["projectsDir"] = storage["coreSettings"]["projects_dir"]["value"]

            # skip non-existing recent projects
            storage["recentProjects"] = list(
                set(
                    str(Path(p).resolve())
                    for p in storage.get("recentProjects", [])
                    if is_platformio_project(p)
                )
            )

            state["storage"] = storage
            state.modified = False  # skip saving extra fields
            return state.as_dict()

    @staticmethod
    def get_state():
        return AppRPC.load_state()

    @staticmethod
    def save_state(state):
        with app.State(AppRPC.get_state_path(), lock=True) as s:
            s.clear()
            s.update(state)
            storage = s.get("storage", {})
            for k in AppRPC.IGNORE_STORAGE_KEYS:
                if k in storage:
                    del storage[k]
        return True
