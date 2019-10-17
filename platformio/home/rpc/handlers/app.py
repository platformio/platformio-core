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

from __future__ import absolute_import

from os.path import join

from platformio import __version__, app, fs, util
from platformio.project.helpers import get_project_core_dir, is_platformio_project


class AppRPC(object):

    APPSTATE_PATH = join(get_project_core_dir(), "homestate.json")

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
    def load_state():
        with app.State(AppRPC.APPSTATE_PATH, lock=True) as state:
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
            storage["recentProjects"] = [
                p for p in storage.get("recentProjects", []) if is_platformio_project(p)
            ]

            state["storage"] = storage
            state.modified = False  # skip saving extra fields
            return state.as_dict()

    @staticmethod
    def get_state():
        return AppRPC.load_state()

    @staticmethod
    def save_state(state):
        with app.State(AppRPC.APPSTATE_PATH, lock=True) as s:
            s.clear()
            s.update(state)
            storage = s.get("storage", {})
            for k in AppRPC.IGNORE_STORAGE_KEYS:
                if k in storage:
                    del storage[k]
        return True
