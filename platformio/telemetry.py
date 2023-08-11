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
import os
import queue
import re
import sys
import threading
import time
import traceback
from collections import deque

import requests

from platformio import __title__, __version__, app, exception, fs, util
from platformio.cli import PlatformioCLI
from platformio.debug.config.base import DebugConfigBase
from platformio.http import HTTPSession
from platformio.proc import is_ci

KEEP_MAX_REPORTS = 100
SEND_MAX_EVENTS = 25


class MeasurementProtocol:
    def __init__(self, events=None):
        self.client_id = app.get_cid()
        self._events = events or []
        self._user_properties = {}

        self.set_user_property("systype", util.get_systype())
        created_at = app.get_state_item("created_at", None)
        if created_at:
            self.set_user_property("created_at", int(created_at))

    @staticmethod
    def event_to_dict(name, params, timestamp=None):
        event = {"name": name, "params": params}
        if timestamp is not None:
            event["timestamp"] = timestamp
        return event

    def set_user_property(self, name, value):
        self._user_properties[name] = value

    def add_event(self, name, params):
        self._events.append(self.event_to_dict(name, params))

    def to_payload(self):
        return {
            "client_id": self.client_id,
            "user_properties": self._user_properties,
            "events": self._events,
        }


@util.singleton
class TelemetryLogger:
    def __init__(self):
        self._events = deque()

        self._sender_thread = None
        self._sender_queue = queue.Queue()
        self._sender_terminated = False

        self._http_session = HTTPSession()
        self._http_offline = False

    def close(self):
        self._http_session.close()

    def log_event(self, name, params, timestamp=None, instant_sending=False):
        if not app.get_setting("enable_telemetry") or app.get_session_var(
            "pause_telemetry"
        ):
            return None
        timestamp = timestamp or int(time.time())
        self._events.append(
            MeasurementProtocol.event_to_dict(name, params, timestamp=timestamp)
        )
        if self._http_offline:  # if network is off-line
            return False
        if instant_sending:
            self.send()
        return True

    def send(self):
        if not self._events or self._sender_terminated:
            return
        if not self._sender_thread:
            self._sender_thread = threading.Thread(
                target=self._sender_worker, daemon=True
            )
            self._sender_thread.start()
        while self._events:
            events = []
            try:
                while len(events) < SEND_MAX_EVENTS:
                    events.append(self._events.popleft())
            except IndexError:
                pass
            self._sender_queue.put(events)

    def _sender_worker(self):
        while True:
            if self._sender_terminated:
                return
            try:
                events = self._sender_queue.get()
                if not self._commit_events(events):
                    self._events.extend(events)
                self._sender_queue.task_done()
            except (queue.Empty, ValueError):
                pass

    def _commit_events(self, events):
        if self._http_offline:
            return False
        mp = MeasurementProtocol(events)
        payload = mp.to_payload()
        # print("_commit_payload", payload)
        try:
            r = self._http_session.post(
                "https://collector.platformio.org/collect",
                json=payload,
                timeout=(2, 5),  # connect, read
            )
            r.raise_for_status()
            return True
        except requests.exceptions.HTTPError as exc:
            # skip Bad Request
            if exc.response.status_code >= 400 and exc.response.status_code < 500:
                return True
        except:  # pylint: disable=bare-except
            pass
        self._http_offline = True
        return False

    def terminate_sender(self):
        self._sender_terminated = True

    def is_sending(self):
        return self._sender_queue.unfinished_tasks

    def get_unsent_events(self):
        result = list(self._events)
        try:
            while True:
                result.extend(self._sender_queue.get_nowait())
        except queue.Empty:
            pass
        return result


def log_event(name, params, instant_sending=False):
    TelemetryLogger().log_event(name, params, instant_sending=instant_sending)


def on_cmd_start(cmd_ctx):
    process_postponed_logs()
    log_command(cmd_ctx)


def on_exit():
    TelemetryLogger().send()


def log_command(ctx):
    params = {
        "path_args": PlatformioCLI.reveal_cmd_path_args(ctx),
    }
    if is_ci():
        params["ci_actor"] = resolve_ci_actor() or "Unknown"
    log_event("cmd_run", params)


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
        option: config.get(section, option)
        for option in non_sensitive_data
        if config.has_option(section, option)
    }
    params["pid"] = app.get_project_id(os.path.dirname(config.path))
    params["platform_name"] = platform.name
    params["platform_version"] = platform.version
    return params


def log_platform_run(platform, project_config, project_env, targets=None):
    params = dump_project_env_params(project_config, project_env, platform)
    if targets:
        params["targets"] = targets
    log_event("platform_run", params, instant_sending=True)


def log_exception(exc):
    skip_conditions = [
        isinstance(exc, cls)
        for cls in (
            IOError,
            exception.ReturnErrorCode,
            exception.UserSideException,
        )
    ]
    skip_conditions.append(not isinstance(exc, Exception))
    if any(skip_conditions):
        return
    is_fatal = any(
        [
            not isinstance(exc, exception.PlatformioException),
            "Error" in exc.__class__.__name__,
        ]
    )

    def _strip_module_path(match):
        module_path = match.group(1).replace(fs.get_source_dir() + os.sep, "")
        sp_folder_name = "site-packages"
        sp_pos = module_path.find(sp_folder_name)
        if sp_pos != -1:
            module_path = module_path[sp_pos + len(sp_folder_name) + 1 :]
        module_path = fs.to_unix_path(module_path)
        return f'File "{module_path}",'

    trace = re.sub(
        r'File "([^"]+)",',
        _strip_module_path,
        traceback.format_exc(),
        flags=re.MULTILINE,
    )

    params = {
        "name": exc.__class__.__name__,
        "description": str(exc),
        "traceback": trace,
        "cmd_args": sys.argv[1:],
        "is_fatal": is_fatal,
    }
    log_event("exception", params)


def log_debug_started(debug_config: DebugConfigBase):
    log_event(
        "debug_started",
        dump_project_env_params(
            debug_config.project_config, debug_config.env_name, debug_config.platform
        ),
    )


def log_debug_exception(exc, debug_config: DebugConfigBase):
    # cleanup sensitive information, such as paths
    description = fs.to_unix_path(str(exc))
    description = re.sub(
        r'(^|\s+|")(?:[a-z]\:)?((/[^"/]+)+)(\s+|"|$)',
        lambda m: " %s " % os.path.join(*m.group(2).split("/")[-2:]),
        description,
        re.I | re.M,
    )
    params = {
        "name": exc.__class__.__name__,
        "description": description.strip(),
    }
    params.update(
        dump_project_env_params(
            debug_config.project_config, debug_config.env_name, debug_config.platform
        )
    )
    log_event("debug_exception", params)


@atexit.register
def _finalize():
    timeout = 1000  # msec
    elapsed = 0
    telemetry = TelemetryLogger()
    telemetry.terminate_sender()
    try:
        while elapsed < timeout:
            if not telemetry.is_sending():
                break
            time.sleep(0.2)
            elapsed += 200
    except KeyboardInterrupt:
        pass
    postpone_events(telemetry.get_unsent_events())
    telemetry.close()


def load_postponed_events():
    state_path = app.resolve_state_path(
        "cache_dir", "telemetry.json", ensure_dir_exists=False
    )
    if not os.path.isfile(state_path):
        return []
    with app.State(state_path) as state:
        return state.get("events", [])


def save_postponed_events(events):
    state_path = app.resolve_state_path("cache_dir", "telemetry.json")
    if not events:
        try:
            if os.path.isfile(state_path):
                os.remove(state_path)
        except:  # pylint: disable=bare-except
            pass
        return None
    with app.State(state_path, lock=True) as state:
        state["events"] = events
        state.modified = True
    return True


def postpone_events(events):
    if not events:
        return None
    postponed_events = load_postponed_events() or []
    timestamp = int(time.time())
    for event in events:
        if "timestamp" not in event:
            event["timestamp"] = timestamp
        postponed_events.append(event)
    save_postponed_events(postponed_events[KEEP_MAX_REPORTS * -1 :])
    return True


def process_postponed_logs():
    events = load_postponed_events()
    if not events:
        return None
    save_postponed_events([])  # clean
    telemetry = TelemetryLogger()
    for event in events:
        if set(["name", "params", "timestamp"]) <= set(event.keys()):
            telemetry.log_event(
                event["name"],
                event["params"],
                timestamp=event["timestamp"],
                instant_sending=False,
            )
    telemetry.send()
    return True
