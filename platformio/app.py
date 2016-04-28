# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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
from copy import deepcopy
from os import environ, getenv
from os.path import getmtime, isfile, join
from time import time

from lockfile import LockFile

from platformio import __version__, util
from platformio.exception import InvalidSettingName, InvalidSettingValue

DEFAULT_SETTINGS = {
    "check_platformio_interval": {
        "description": "Check for the new PlatformIO interval (days)",
        "value": 3
    },
    "check_platforms_interval": {
        "description": "Check for the platform updates interval (days)",
        "value": 7
    },
    "check_libraries_interval": {
        "description": "Check for the library updates interval (days)",
        "value": 7
    },
    "auto_update_platforms": {
        "description": "Automatically update platforms (Yes/No)",
        "value": False
    },
    "auto_update_libraries": {
        "description": "Automatically update libraries (Yes/No)",
        "value": False
    },
    "enable_telemetry": {
        "description": (
            "Telemetry service <http://docs.platformio.org/en/latest/"
            "userguide/cmd_settings.html?#enable-telemetry> (Yes/No)"),
        "value": True
    },
    "enable_prompts": {
        "description": (
            "Can PlatformIO communicate with you via prompts: "
            "propose to install platforms which aren't installed yet, "
            "paginate over library search results and etc.)? ATTENTION!!! "
            "If you call PlatformIO like subprocess, "
            "please disable prompts to avoid blocking (Yes/No)"),
        "value": True
    }
}


SESSION_VARS = {
    "command_ctx": None,
    "force_option": False,
    "caller_id": None
}


class State(object):

    def __init__(self, path=None, lock=False):
        self.path = path
        self.lock = lock
        if not self.path:
            self.path = join(util.get_home_dir(), "appstate.json")
        self._state = {}
        self._prev_state = {}
        self._lockfile = None

    def __enter__(self):
        try:
            self._lock_state_file()
            if isfile(self.path):
                self._state = util.load_json(self.path)
        except ValueError:
            self._state = {}
        self._prev_state = deepcopy(self._state)
        return self._state

    def __exit__(self, type_, value, traceback):
        if self._prev_state != self._state:
            with open(self.path, "w") as fp:
                if "dev" in __version__:
                    json.dump(self._state, fp, indent=4)
                else:
                    json.dump(self._state, fp)
        self._unlock_state_file()

    def _lock_state_file(self):
        if not self.lock:
            return
        self._lockfile = LockFile(self.path)

        if (self._lockfile.is_locked() and
                (time() - getmtime(self._lockfile.lock_file)) > 10):
            self._lockfile.break_lock()

        self._lockfile.acquire()

    def _unlock_state_file(self):
        if self._lockfile:
            self._lockfile.release()


def sanitize_setting(name, value):
    if name not in DEFAULT_SETTINGS:
        raise InvalidSettingName(name)

    defdata = DEFAULT_SETTINGS[name]
    try:
        if "validator" in defdata:
            value = defdata['validator']()
        elif isinstance(defdata['value'], bool):
            if not isinstance(value, bool):
                value = str(value).lower() in ("true", "yes", "y", "1")
        elif isinstance(defdata['value'], int):
            value = int(value)
    except Exception:
        raise InvalidSettingValue(value, name)
    return value


def get_state_item(name, default=None):
    with State() as data:
        return data.get(name, default)


def set_state_item(name, value):
    with State(lock=True) as data:
        data[name] = value


def get_setting(name):
    if name == "enable_prompts":
        # disable prompts for Continuous Integration systems
        # and when global "--force" option is set
        if any([util.is_ci(), get_session_var("force_option")]):
            return False

    _env_name = "PLATFORMIO_SETTING_%s" % name.upper()
    if _env_name in environ:
        return sanitize_setting(name, getenv(_env_name))

    with State() as data:
        if "settings" in data and name in data['settings']:
            return data['settings'][name]

    return DEFAULT_SETTINGS[name]['value']


def set_setting(name, value):
    with State(lock=True) as data:
        if "settings" not in data:
            data['settings'] = {}
        data['settings'][name] = sanitize_setting(name, value)


def reset_settings():
    with State(lock=True) as data:
        if "settings" in data:
            del data['settings']


def get_session_var(name, default=None):
    return SESSION_VARS.get(name, default)


def set_session_var(name, value):
    assert name in SESSION_VARS
    SESSION_VARS[name] = value


def is_disabled_progressbar():
    return (not get_setting("enable_prompts") or
            getenv("PLATFORMIO_DISABLE_PROGRESSBAR") == "true")
