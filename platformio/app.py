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

import hashlib
import json
import os
import uuid
from copy import deepcopy
from os import environ, getenv, listdir, remove
from os.path import dirname, getmtime, isdir, isfile, join
from time import time

import requests
from lockfile import LockFailed, LockFile

from platformio import __version__, exception, util
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
    "force_verbose": {
        "description": "Force verbose output when processing environments",
        "value": False
    },
    "enable_ssl": {
        "description": "Enable SSL for PlatformIO Services",
        "value": False
    },
    "enable_cache": {
        "description": "Enable caching for API requests and Library Manager",
        "value": True
    },
    "enable_telemetry": {
        "description":
        ("Telemetry service <http://docs.platformio.org/page/"
         "userguide/cmd_settings.html?#enable-telemetry> (Yes/No)"),
        "value":
        True
    }
}

SESSION_VARS = {"command_ctx": None, "force_option": False, "caller_id": None}


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

        if self._lockfile.is_locked() and \
                (time() - getmtime(self._lockfile.lock_file)) > 10:
            self._lockfile.break_lock()

        try:
            self._lockfile.acquire()
        except LockFailed:
            raise exception.PlatformioException(
                "The directory `{0}` or its parent directory is not owned by "
                "the current user and PlatformIO can not store configuration "
                "data. \nPlease check the permissions and owner of that "
                "directory. Otherwise, please remove manually `{0}` "
                "directory and PlatformIO will create new from the current "
                "user.".format(dirname(self.path)))

    def _unlock_state_file(self):
        if self._lockfile:
            self._lockfile.release()


class ContentCache(object):

    def __init__(self, cache_dir=None):
        self.cache_dir = None
        self._db_path = None
        self._lockfile = None

        if not get_setting("enable_cache"):
            return

        self.cache_dir = cache_dir or join(util.get_home_dir(), ".cache")
        self._db_path = join(self.cache_dir, "db.data")

    def __enter__(self):
        if not self._db_path or not isfile(self._db_path):
            return self

        self.delete()
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def _lock_dbindex(self):
        if not self.cache_dir:
            os.makedirs(self.cache_dir)
        self._lockfile = LockFile(self.cache_dir)
        if self._lockfile.is_locked() and \
                (time() - getmtime(self._lockfile.lock_file)) > 10:
            self._lockfile.break_lock()

        try:
            self._lockfile.acquire()
        except LockFailed:
            return False

        return True

    def _unlock_dbindex(self):
        if self._lockfile:
            self._lockfile.release()
        return True

    def get_cache_path(self, key):
        assert len(key) > 3
        return join(self.cache_dir, key[-2:], key)

    @staticmethod
    def key_from_args(*args):
        h = hashlib.md5()
        for data in args:
            h.update(str(data))
        return h.hexdigest()

    def get(self, key):
        cache_path = self.get_cache_path(key)
        if not isfile(cache_path):
            return None
        with open(cache_path, "rb") as fp:
            data = fp.read()
            if data and data[0] in ("{", "["):
                return json.loads(data)
            return data

    def set(self, key, data, valid):
        cache_path = self.get_cache_path(key)
        if isfile(cache_path):
            self.delete(key)
        if not data:
            return
        if not isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        tdmap = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        assert valid.endswith(tuple(tdmap.keys()))
        expire_time = int(time() + tdmap[valid[-1]] * int(valid[:-1]))

        if not self._lock_dbindex():
            return False

        if not isdir(dirname(cache_path)):
            os.makedirs(dirname(cache_path))
        with open(cache_path, "wb") as fp:
            if isinstance(data, (dict, list)):
                json.dump(data, fp)
            else:
                fp.write(str(data))
        with open(self._db_path, "a") as fp:
            fp.write("%s=%s\n" % (str(expire_time), cache_path))

        return self._unlock_dbindex()

    def delete(self, keys=None):
        """ Keys=None, delete expired items """
        if not keys:
            keys = []
        if not isinstance(keys, list):
            keys = [keys]
        paths_for_delete = [self.get_cache_path(k) for k in keys]
        found = False
        newlines = []
        with open(self._db_path) as fp:
            for line in fp.readlines():
                if "=" not in line:
                    continue
                line = line.strip()
                expire, path = line.split("=")
                if time() < int(expire) and isfile(path) and \
                        path not in paths_for_delete:
                    newlines.append(line)
                    continue
                found = True
                if isfile(path):
                    try:
                        remove(path)
                        if not listdir(dirname(path)):
                            util.rmtree_(dirname(path))
                    except OSError:
                        pass

        if found and self._lock_dbindex():
            with open(self._db_path, "w") as fp:
                fp.write("\n".join(newlines) + "\n")
            self._unlock_dbindex()

        return True

    def clean(self):
        if not self.cache_dir or not isdir(self.cache_dir):
            return
        util.rmtree_(self.cache_dir)


def clean_cache():
    with ContentCache() as cc:
        cc.clean()


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


def delete_state_item(name):
    with State(lock=True) as data:
        if name in data:
            del data[name]


def get_setting(name):
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
    return any([
        get_session_var("force_option"),
        util.is_ci(),
        getenv("PLATFORMIO_DISABLE_PROGRESSBAR") == "true"
    ])


def get_cid():
    cid = get_state_item("cid")
    if not cid:
        _uid = None
        if getenv("C9_UID"):
            _uid = getenv("C9_UID")
        elif getenv("CHE_API", getenv("CHE_API_ENDPOINT")):
            try:
                _uid = requests.get("{api}/user?token={token}".format(
                    api=getenv("CHE_API", getenv("CHE_API_ENDPOINT")),
                    token=getenv("USER_TOKEN"))).json().get("id")
            except:  # pylint: disable=bare-except
                pass
        cid = str(
            uuid.UUID(bytes=hashlib.md5(str(_uid if _uid else uuid.getnode()))
                      .digest()))
        set_state_item("cid", cid)
    return cid
