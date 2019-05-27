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

import json
from os.path import expanduser, isfile, join

from platformio import __version__, app, exception, util
from platformio.compat import path_to_unicode


class AppRPC(object):

    APPSTATE_PATH = join(util.get_home_dir(), "homestate.json")

    @staticmethod
    def load_state():
        state = None
        try:
            if isfile(AppRPC.APPSTATE_PATH):
                state = util.load_json(AppRPC.APPSTATE_PATH)
        except exception.PlatformioException:
            pass
        if not isinstance(state, dict):
            state = {}
        storage = state.get("storage", {})

        # base data
        caller_id = app.get_session_var("caller_id")
        storage['cid'] = app.get_cid()
        storage['coreVersion'] = __version__
        storage['coreSystype'] = util.get_systype()
        storage['coreCaller'] = (str(caller_id).lower() if caller_id else None)
        storage['coreSettings'] = {
            name: {
                "description": data['description'],
                "default_value": data['value'],
                "value": app.get_setting(name)
            }
            for name, data in app.DEFAULT_SETTINGS.items()
        }

        # encode to UTF-8
        for key in storage['coreSettings']:
            if not key.endswith("dir"):
                continue
            storage['coreSettings'][key]['default_value'] = path_to_unicode(
                storage['coreSettings'][key]['default_value'])
            storage['coreSettings'][key]['value'] = path_to_unicode(
                storage['coreSettings'][key]['value'])
        storage['homeDir'] = path_to_unicode(expanduser("~"))
        storage['projectsDir'] = storage['coreSettings']['projects_dir'][
            'value']

        # skip non-existing recent projects
        storage['recentProjects'] = [
            p for p in storage.get("recentProjects", [])
            if util.is_platformio_project(p)
        ]

        state['storage'] = storage
        return state

    @staticmethod
    def get_state():
        return AppRPC.load_state()

    def save_state(self, state):
        with open(self.APPSTATE_PATH, "w") as fp:
            json.dump(state, fp)
        return True
