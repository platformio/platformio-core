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

import atexit
import hashlib
import os
import platform as python_platform
import queue
import re
import threading
from collections import deque
from time import sleep, time
from traceback import format_exc

import requests

from platformio import __title__, __version__, app, exception, util
from platformio.cli import PlatformioCLI
from platformio.compat import hashlib_encode_data
from platformio.debug.config.base import DebugConfigBase
from platformio.http import HTTPSession, ensure_internet_on
from platformio.proc import is_ci, is_container

KEEP_MAX_REPORTS = 100
SEND_MAX_EVENTS = 25


class MeasurementProtocol:
    def __init__(self):
        self._user_properties = {}
        self._events = []

        caller_id = app.get_session_var("caller_id")
        if caller_id:
            self.set_user_property("pio_caller_id", caller_id)
        self.set_user_property("pio_core_version", __version__)
        self.set_user_property(
            "pio_human_actor", int(bool(caller_id or not (is_ci() or is_container())))
        )
        self.set_user_property("pio_systype", util.get_systype())
        created_at = app.get_state_item("created_at", None)
        if created_at:
            self.set_user_property("pio_created_at", int(created_at))

    def set_user_property(self, name, value):
        self._user_properties[name] = {"value": value}

    def add_event(self, name, params):
        params["engagement_time_msec"] = params.get("engagement_time_msec", 1)
        self._events.append({"name": name, "params": params})

    def to_payload(self):
        return {
            "client_id": app.get_cid(),
            "non_personalized_ads": True,
            "user_properties": self._user_properties,
            "events": self._events,
        }


@util.singleton
class TelemetryLogger:
    MAX_WORKERS = 5

    def __init__(self):
        self._queue = queue.LifoQueue()
        self._failedque = deque()
        self._http_session = HTTPSession()
        self._http_offline = False
        self._workers = []

    def log(self, payload):
        if not app.get_setting("enable_telemetry"):
            return None

        # if network is off-line
        if self._http_offline:
            self._failedque.append(payload)
            return False

        self._queue.put(payload)
        self._tune_workers()
        return True

    def in_wait(self):
        return self._queue.unfinished_tasks

    def get_unprocessed(self):
        items = list(self._failedque)
        try:
            while True:
                items.append(self._queue.get_nowait())
        except queue.Empty:
            pass
        return items

    def _tune_workers(self):
        for i, w in enumerate(self._workers):
            if not w.is_alive():
                del self._workers[i]

        need_nums = min(self._queue.qsize(), self.MAX_WORKERS)
        active_nums = len(self._workers)
        if need_nums <= active_nums:
            return

        for i in range(need_nums - active_nums):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            self._workers.append(t)

    def _worker(self):
        while True:
            try:
                item = self._queue.get()
                _item = item.copy()
                if "qt" not in _item:
                    _item["qt"] = time()
                self._failedque.append(_item)
                if self._send(item):
                    self._failedque.remove(_item)
                self._queue.task_done()
            except:  # pylint: disable=W0702
                pass

    def _send(self, payload):
        if self._http_offline:
            return False
        try:
            r = self._http_session.post(
                "https://www.google-analytics.com/mp/collect",
                params={
                    "measurement_id": util.decrypt_message(
                        __title__, "t5m7rKu6tbqwx8Cw"
                    ),
                    "api_secret": util.decrypt_message(
                        __title__, "48SRy5rmut28ptm7zLjS5sa7tdmhrQ=="
                    ),
                },
                json=payload,
                timeout=1,
            )
            r.raise_for_status()
            return True
        except requests.exceptions.HTTPError as exc:
            # skip Bad Request
            if 400 >= exc.response.status_code < 500:
                return True
        except:  # pylint: disable=bare-except
            pass
        self._http_offline = True
        return False


def log_event(name, params):
    mp = MeasurementProtocol()
    mp.add_event(name, params)
    TelemetryLogger().log(mp.to_payload())


def log_command(ctx):
    path_args = PlatformioCLI.reveal_cmd_path_args(ctx)
    params = {
        "page_title": " ".join([arg.title() for arg in path_args]),
        "page_path": "/".join(path_args),
        "pio_user_agent": app.get_user_agent(),
        "pio_python_version": python_platform.python_version(),
    }
    if is_ci():
        params["ci_actor"] = resolve_ci_actor() or "Unknown"
    log_event("page_view", params)


def resolve_ci_actor():
    known_cis = (
        "GITHUB_ACTIONS",
        "TRAVIS",
        "APPVEYOR",
        "GITLAB_CI",
        "CIRCLECI",
        "SHIPPABLE",
        "DRONE",
    )
    for name in known_cis:
        if os.getenv(name, "false").lower() == "true":
            return name
    return None


def log_exception(e):
    skip_conditions = [
        isinstance(e, cls)
        for cls in (
            IOError,
            exception.ReturnErrorCode,
            exception.UserSideException,
        )
    ]
    if any(skip_conditions):
        return
    is_fatal = any(
        [
            not isinstance(e, exception.PlatformioException),
            "Error" in e.__class__.__name__,
        ]
    )
    description = "%s: %s" % (
        type(e).__name__,
        " ".join(reversed(format_exc().split("\n"))) if is_fatal else str(e),
    )
    params = {
        "description": description[:100].strip(),
        "is_fatal": int(is_fatal),
        "pio_user_agent": app.get_user_agent(),
    }
    log_event("pio_exception", params)


def dump_project_env_params(config, env, platform):
    non_sensitive_data = [
        "platform",
        "framework",
        "board",
        "upload_protocol",
        "check_tool",
        "debug_tool",
        "test_framework",
    ]
    section = f"env:{env}"
    params = {
        f"pio_{option}": config.get(section, option)
        for option in non_sensitive_data
        if config.has_option(section, option)
    }
    params["pio_pid"] = hashlib.sha1(hashlib_encode_data(config.path)).hexdigest()
    params["pio_platform_name"] = platform.name
    params["pio_platform_version"] = platform.version
    params["pio_framework"] = params.get("pio_framework", "__bare_metal__")
    # join multi-value options
    for key, value in params.items():
        if isinstance(value, list):
            params[key] = ", ".join(value)
    return params


def log_platform_run(platform, project_config, project_env, targets=None):
    params = dump_project_env_params(project_config, project_env, platform)
    if targets:
        params["targets"] = ", ".join(targets)
    log_event("pio_platform_run", params)


def log_debug_started(debug_config: DebugConfigBase):
    log_event(
        "pio_debug_started",
        dump_project_env_params(
            debug_config.project_config, debug_config.env_name, debug_config.platform
        ),
    )


def log_debug_exception(description, debug_config: DebugConfigBase):
    # cleanup sensitive information, such as paths
    description = description.replace("Traceback (most recent call last):", "")
    description = description.replace("\\", "/")
    description = re.sub(
        r'(^|\s+|")(?:[a-z]\:)?((/[^"/]+)+)(\s+|"|$)',
        lambda m: " %s " % os.path.join(*m.group(2).split("/")[-2:]),
        description,
        re.I | re.M,
    )
    description = re.sub(r"\s+", " ", description, flags=re.M)
    params = {
        "description": description[:100].strip(),
        "pio_user_agent": app.get_user_agent(),
    }
    params.update(
        dump_project_env_params(
            debug_config.project_config, debug_config.env_name, debug_config.platform
        )
    )
    log_event("pio_debug_exception", params)


@atexit.register
def _finalize():
    timeout = 1000  # msec
    elapsed = 0
    try:
        while elapsed < timeout:
            if not TelemetryLogger().in_wait():
                break
            sleep(0.2)
            elapsed += 200
        postpone_logs(TelemetryLogger().get_unprocessed())
    except KeyboardInterrupt:
        pass


def load_postponed_events():
    state_path = app.resolve_state_path(
        "cache_dir", "telemetry.json", ensure_dir_exists=False
    )
    if not os.path.isfile(state_path):
        return []
    with app.State(state_path) as state:
        return state.get("events", [])


def save_postponed_events(items):
    state_path = app.resolve_state_path("cache_dir", "telemetry.json")
    if not items:
        try:
            if os.path.isfile(state_path):
                os.remove(state_path)
        except:  # pylint: disable=bare-except
            pass
        return None
    with app.State(state_path, lock=True) as state:
        state["events"] = items
        state.modified = True
    return True


def postpone_logs(payloads):
    if not payloads:
        return None
    postponed_events = load_postponed_events() or []
    timestamp_micros = int(time() * 1000000)
    for payload in payloads:
        for event in payload.get("events", []):
            event["timestamp_micros"] = timestamp_micros
            postponed_events.append(event)
    save_postponed_events(postponed_events[KEEP_MAX_REPORTS * -1 :])
    return True


def resend_postponed_logs():
    events = load_postponed_events()
    if not events or not ensure_internet_on():
        return None
    save_postponed_events(events[SEND_MAX_EVENTS:])  # clean
    mp = MeasurementProtocol()
    payload = mp.to_payload()
    payload["events"] = events[0:SEND_MAX_EVENTS]
    TelemetryLogger().log(payload)
    if len(events) > SEND_MAX_EVENTS:
        resend_postponed_logs()
    return True
