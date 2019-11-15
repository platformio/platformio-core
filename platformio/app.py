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

import codecs
import hashlib
import os
import uuid
from os import environ, getenv, listdir, remove
from os.path import dirname, isdir, isfile, join, realpath
from time import time

import requests

from platformio import exception, fs, lockfile
from platformio.compat import WINDOWS, dump_json_to_unicode, hashlib_encode_data
from platformio.proc import is_ci
from platformio.project.helpers import (
    get_default_projects_dir,
    get_project_cache_dir,
    get_project_core_dir,
)


def projects_dir_validate(projects_dir):
    assert isdir(projects_dir)
    return realpath(projects_dir)


DEFAULT_SETTINGS = {
    "auto_update_libraries": {
        "description": "Automatically update libraries (Yes/No)",
        "value": False,
    },
    "auto_update_platforms": {
        "description": "Automatically update platforms (Yes/No)",
        "value": False,
    },
    "check_libraries_interval": {
        "description": "Check for the library updates interval (days)",
        "value": 7,
    },
    "check_platformio_interval": {
        "description": "Check for the new PlatformIO interval (days)",
        "value": 3,
    },
    "check_platforms_interval": {
        "description": "Check for the platform updates interval (days)",
        "value": 7,
    },
    "enable_cache": {
        "description": "Enable caching for API requests and Library Manager",
        "value": True,
    },
    "strict_ssl": {"description": "Strict SSL for PlatformIO Services", "value": False},
    "enable_telemetry": {
        "description": ("Telemetry service <http://bit.ly/pio-telemetry> (Yes/No)"),
        "value": True,
    },
    "force_verbose": {
        "description": "Force verbose output when processing environments",
        "value": False,
    },
    "projects_dir": {
        "description": "Default location for PlatformIO projects (PIO Home)",
        "value": get_default_projects_dir(),
        "validator": projects_dir_validate,
    },
}

SESSION_VARS = {
    "command_ctx": None,
    "force_option": False,
    "caller_id": None,
    "custom_project_conf": None,
}


class State(object):
    def __init__(self, path=None, lock=False):
        self.path = path
        self.lock = lock
        if not self.path:
            self.path = join(get_project_core_dir(), "appstate.json")
        self._storage = {}
        self._lockfile = None
        self.modified = False

    def __enter__(self):
        try:
            self._lock_state_file()
            if isfile(self.path):
                self._storage = fs.load_json(self.path)
            assert isinstance(self._storage, dict)
        except (
            AssertionError,
            ValueError,
            UnicodeDecodeError,
            exception.InvalidJSONFile,
        ):
            self._storage = {}
        return self

    def __exit__(self, type_, value, traceback):
        if self.modified:
            try:
                with open(self.path, "w") as fp:
                    fp.write(dump_json_to_unicode(self._storage))
            except IOError:
                raise exception.HomeDirPermissionsError(get_project_core_dir())
        self._unlock_state_file()

    def _lock_state_file(self):
        if not self.lock:
            return
        self._lockfile = lockfile.LockFile(self.path)
        try:
            self._lockfile.acquire()
        except IOError:
            raise exception.HomeDirPermissionsError(dirname(self.path))

    def _unlock_state_file(self):
        if hasattr(self, "_lockfile") and self._lockfile:
            self._lockfile.release()

    def __del__(self):
        self._unlock_state_file()

    # Dictionary Proxy

    def as_dict(self):
        return self._storage

    def get(self, key, default=True):
        return self._storage.get(key, default)

    def update(self, *args, **kwargs):
        self.modified = True
        return self._storage.update(*args, **kwargs)

    def clear(self):
        return self._storage.clear()

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        self.modified = True
        self._storage[key] = value

    def __delitem__(self, key):
        self.modified = True
        del self._storage[key]

    def __contains__(self, item):
        return item in self._storage


class ContentCache(object):
    def __init__(self, cache_dir=None):
        self.cache_dir = None
        self._db_path = None
        self._lockfile = None

        self.cache_dir = cache_dir or get_project_cache_dir()
        self._db_path = join(self.cache_dir, "db.data")

    def __enter__(self):
        self.delete()
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def _lock_dbindex(self):
        if not self.cache_dir:
            os.makedirs(self.cache_dir)
        self._lockfile = lockfile.LockFile(self.cache_dir)
        try:
            self._lockfile.acquire()
        except:  # pylint: disable=bare-except
            return False

        return True

    def _unlock_dbindex(self):
        if self._lockfile:
            self._lockfile.release()
        return True

    def get_cache_path(self, key):
        assert "/" not in key and "\\" not in key
        key = str(key)
        assert len(key) > 3
        return join(self.cache_dir, key[-2:], key)

    @staticmethod
    def key_from_args(*args):
        h = hashlib.md5()
        for arg in args:
            if arg:
                h.update(hashlib_encode_data(arg))
        return h.hexdigest()

    def get(self, key):
        cache_path = self.get_cache_path(key)
        if not isfile(cache_path):
            return None
        with codecs.open(cache_path, "rb", encoding="utf8") as fp:
            return fp.read()

    def set(self, key, data, valid):
        if not get_setting("enable_cache"):
            return False
        cache_path = self.get_cache_path(key)
        if isfile(cache_path):
            self.delete(key)
        if not data:
            return False
        if not isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        tdmap = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        assert valid.endswith(tuple(tdmap))
        expire_time = int(time() + tdmap[valid[-1]] * int(valid[:-1]))

        if not self._lock_dbindex():
            return False

        if not isdir(dirname(cache_path)):
            os.makedirs(dirname(cache_path))
        try:
            with codecs.open(cache_path, "wb", encoding="utf8") as fp:
                fp.write(data)
            with open(self._db_path, "a") as fp:
                fp.write("%s=%s\n" % (str(expire_time), cache_path))
        except UnicodeError:
            if isfile(cache_path):
                try:
                    remove(cache_path)
                except OSError:
                    pass

        return self._unlock_dbindex()

    def delete(self, keys=None):
        """ Keys=None, delete expired items """
        if not isfile(self._db_path):
            return None
        if not keys:
            keys = []
        if not isinstance(keys, list):
            keys = [keys]
        paths_for_delete = [self.get_cache_path(k) for k in keys]
        found = False
        newlines = []
        with open(self._db_path) as fp:
            for line in fp.readlines():
                line = line.strip()
                if "=" not in line:
                    continue
                expire, path = line.split("=")
                try:
                    if (
                        time() < int(expire)
                        and isfile(path)
                        and path not in paths_for_delete
                    ):
                        newlines.append(line)
                        continue
                except ValueError:
                    pass
                found = True
                if isfile(path):
                    try:
                        remove(path)
                        if not listdir(dirname(path)):
                            fs.rmtree(dirname(path))
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
        fs.rmtree(self.cache_dir)


def clean_cache():
    with ContentCache() as cc:
        cc.clean()


def sanitize_setting(name, value):
    if name not in DEFAULT_SETTINGS:
        raise exception.InvalidSettingName(name)

    defdata = DEFAULT_SETTINGS[name]
    try:
        if "validator" in defdata:
            value = defdata["validator"](value)
        elif isinstance(defdata["value"], bool):
            if not isinstance(value, bool):
                value = str(value).lower() in ("true", "yes", "y", "1")
        elif isinstance(defdata["value"], int):
            value = int(value)
    except Exception:
        raise exception.InvalidSettingValue(value, name)
    return value


def get_state_item(name, default=None):
    with State() as state:
        return state.get(name, default)


def set_state_item(name, value):
    with State(lock=True) as state:
        state[name] = value
        state.modified = True


def delete_state_item(name):
    with State(lock=True) as state:
        if name in state:
            del state[name]


def get_setting(name):
    _env_name = "PLATFORMIO_SETTING_%s" % name.upper()
    if _env_name in environ:
        return sanitize_setting(name, getenv(_env_name))

    with State() as state:
        if "settings" in state and name in state["settings"]:
            return state["settings"][name]

    return DEFAULT_SETTINGS[name]["value"]


def set_setting(name, value):
    with State(lock=True) as state:
        if "settings" not in state:
            state["settings"] = {}
        state["settings"][name] = sanitize_setting(name, value)
        state.modified = True


def reset_settings():
    with State(lock=True) as state:
        if "settings" in state:
            del state["settings"]


def get_session_var(name, default=None):
    return SESSION_VARS.get(name, default)


def set_session_var(name, value):
    assert name in SESSION_VARS
    SESSION_VARS[name] = value


def is_disabled_progressbar():
    return any(
        [
            get_session_var("force_option"),
            is_ci(),
            getenv("PLATFORMIO_DISABLE_PROGRESSBAR") == "true",
        ]
    )


def get_cid():
    cid = get_state_item("cid")
    if cid:
        return cid
    uid = None
    if getenv("C9_UID"):
        uid = getenv("C9_UID")
    elif getenv("CHE_API", getenv("CHE_API_ENDPOINT")):
        try:
            uid = (
                requests.get(
                    "{api}/user?token={token}".format(
                        api=getenv("CHE_API", getenv("CHE_API_ENDPOINT")),
                        token=getenv("USER_TOKEN"),
                    )
                )
                .json()
                .get("id")
            )
        except:  # pylint: disable=bare-except
            pass
    if not uid:
        uid = uuid.getnode()
    cid = uuid.UUID(bytes=hashlib.md5(hashlib_encode_data(uid)).digest())
    cid = str(cid)
    if WINDOWS or os.getuid() > 0:  # pylint: disable=no-member
        set_state_item("cid", cid)
    return cid
