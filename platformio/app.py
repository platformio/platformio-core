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

import getpass
import hashlib
import json
import os
import platform
import socket
import uuid
from os.path import dirname, isdir, isfile, join, realpath

from platformio import __version__, exception, fs, proc
from platformio.compat import IS_WINDOWS, hashlib_encode_data
from platformio.package.lockfile import LockFile
from platformio.project.helpers import get_default_projects_dir, get_project_core_dir


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
    "check_prune_system_threshold": {
        "description": "Check for pruning unnecessary data threshold (megabytes)",
        "value": 1024,
    },
    "enable_cache": {
        "description": "Enable caching for HTTP API requests",
        "value": True,
    },
    "enable_telemetry": {
        "description": ("Telemetry service <http://bit.ly/pio-telemetry> (Yes/No)"),
        "value": True,
    },
    "force_verbose": {
        "description": "Force verbose output when processing environments",
        "value": False,
    },
    "projects_dir": {
        "description": "Default location for PlatformIO projects (PlatformIO Home)",
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
                with open(self.path, mode="w", encoding="utf8") as fp:
                    fp.write(json.dumps(self._storage))
            except IOError:
                raise exception.HomeDirPermissionsError(get_project_core_dir())
        self._unlock_state_file()

    def _lock_state_file(self):
        if not self.lock:
            return
        self._lockfile = LockFile(self.path)
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

    def keys(self):
        return self._storage.keys()

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
    if _env_name in os.environ:
        return sanitize_setting(name, os.getenv(_env_name))

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
            proc.is_ci(),
            os.getenv("PLATFORMIO_DISABLE_PROGRESSBAR") == "true",
        ]
    )


def get_cid():
    # pylint: disable=import-outside-toplevel
    from platformio.clients.http import fetch_remote_content

    cid = get_state_item("cid")
    if cid:
        return cid
    uid = None
    if os.getenv("C9_UID"):
        uid = os.getenv("C9_UID")
    elif os.getenv("GITPOD_GIT_USER_NAME"):
        uid = os.getenv("GITPOD_GIT_USER_NAME")
    elif os.getenv("CHE_API", os.getenv("CHE_API_ENDPOINT")):
        try:
            uid = json.loads(
                fetch_remote_content(
                    "{api}/user?token={token}".format(
                        api=os.getenv("CHE_API", os.getenv("CHE_API_ENDPOINT")),
                        token=os.getenv("USER_TOKEN"),
                    )
                )
            ).get("id")
        except:  # pylint: disable=bare-except
            pass
    if not uid:
        uid = uuid.getnode()
    cid = uuid.UUID(bytes=hashlib.md5(hashlib_encode_data(uid)).digest())
    cid = str(cid)
    if IS_WINDOWS or os.getuid() > 0:  # pylint: disable=no-member
        set_state_item("cid", cid)
    return cid


def get_user_agent():
    data = [
        "PlatformIO/%s" % __version__,
        "CI/%d" % int(proc.is_ci()),
        "Container/%d" % int(proc.is_container()),
    ]
    if get_session_var("caller_id"):
        data.append("Caller/%s" % get_session_var("caller_id"))
    if os.getenv("PLATFORMIO_IDE"):
        data.append("IDE/%s" % os.getenv("PLATFORMIO_IDE"))
    data.append("Python/%s" % platform.python_version())
    data.append("Platform/%s" % platform.platform())
    return " ".join(data)


def get_host_id():
    h = hashlib.sha1(hashlib_encode_data(get_cid()))
    try:
        username = getpass.getuser()
        h.update(hashlib_encode_data(username))
    except:  # pylint: disable=bare-except
        pass
    return h.hexdigest()


def get_host_name():
    return str(socket.gethostname())[:255]
