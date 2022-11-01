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
import json
import os
import queue
import re
import shutil
import sys
import threading
from collections import deque
from time import sleep, time
from traceback import format_exc

import requests

from platformio import __version__, app, exception, util
from platformio.cli import PlatformioCLI
from platformio.compat import hashlib_encode_data, string_types
from platformio.http import HTTPSession
from platformio.proc import is_ci, is_container
from platformio.project.helpers import is_platformio_project


class TelemetryBase:
    def __init__(self):
        self._params = {}

    def __getitem__(self, name):
        return self._params.get(name, None)

    def __setitem__(self, name, value):
        self._params[name] = value

    def __delitem__(self, name):
        if name in self._params:
            del self._params[name]

    def send(self, hittype):
        raise NotImplementedError()


class MeasurementProtocol(TelemetryBase):

    TID = "UA-1768265-9"
    PARAMS_MAP = {
        "screen_name": "cd",
        "event_category": "ec",
        "event_action": "ea",
        "event_label": "el",
        "event_value": "ev",
    }

    def __init__(self):
        super().__init__()
        self["v"] = 1
        self["tid"] = self.TID
        self["cid"] = app.get_cid()

        try:
            self["sr"] = "%dx%d" % shutil.get_terminal_size()
        except ValueError:
            pass

        self._prefill_screen_name()
        self._prefill_appinfo()
        self._prefill_sysargs()
        self._prefill_custom_data()

    def __getitem__(self, name):
        if name in self.PARAMS_MAP:
            name = self.PARAMS_MAP[name]
        return super().__getitem__(name)

    def __setitem__(self, name, value):
        if name in self.PARAMS_MAP:
            name = self.PARAMS_MAP[name]
        super().__setitem__(name, value)

    def _prefill_appinfo(self):
        self["av"] = __version__
        self["an"] = app.get_user_agent()

    def _prefill_sysargs(self):
        args = []
        for arg in sys.argv[1:]:
            arg = str(arg)
            if arg == "account":  # ignore account cmd which can contain username
                return
            if any(("@" in arg, "/" in arg, "\\" in arg)):
                arg = "***"
            args.append(arg.lower())
        self["cd3"] = " ".join(args)

    def _prefill_custom_data(self):
        def _filter_args(items):
            result = []
            stop = False
            for item in items:
                item = str(item).lower()
                result.append(item)
                if stop:
                    break
                if item == "account":
                    stop = True
            return result

        caller_id = str(app.get_session_var("caller_id"))
        self["cd1"] = util.get_systype()
        self["cd4"] = 1 if (not is_ci() and (caller_id or not is_container())) else 0
        if caller_id:
            self["cd5"] = caller_id.lower()

    def _prefill_screen_name(self):
        def _first_arg_from_list(args_, list_):
            for _arg in args_:
                if _arg in list_:
                    return _arg
            return None

        args = []
        for arg in PlatformioCLI.leftover_args:
            if not isinstance(arg, string_types):
                arg = str(arg)
            if not arg.startswith("-"):
                args.append(arg.lower())
        if not args:
            return

        cmd_path = args[:1]
        if args[0] in (
            "access",
            "account",
            "device",
            "org",
            "package",
            "pkg",
            "platform",
            "project",
            "settings",
            "system",
            "team",
        ):
            cmd_path = args[:2]
        if args[0] == "lib" and len(args) > 1:
            lib_subcmds = (
                "builtin",
                "install",
                "list",
                "register",
                "search",
                "show",
                "stats",
                "uninstall",
                "update",
            )
            sub_cmd = _first_arg_from_list(args[1:], lib_subcmds)
            if sub_cmd:
                cmd_path.append(sub_cmd)
        elif args[0] == "remote" and len(args) > 1:
            remote_subcmds = ("agent", "device", "run", "test")
            sub_cmd = _first_arg_from_list(args[1:], remote_subcmds)
            if sub_cmd:
                cmd_path.append(sub_cmd)
                if len(args) > 2 and sub_cmd in ("agent", "device"):
                    remote2_subcmds = ("list", "start", "monitor")
                    sub_cmd = _first_arg_from_list(args[2:], remote2_subcmds)
                    if sub_cmd:
                        cmd_path.append(sub_cmd)
        self["screen_name"] = " ".join([p.title() for p in cmd_path])

    def _ignore_hit(self):
        if not app.get_setting("enable_telemetry"):
            return True
        if self["ea"] in ("Idedata", "__Idedata"):
            return True
        return False

    def send(self, hittype):
        if self._ignore_hit():
            return
        self["t"] = hittype
        # correct queue time
        if "qt" in self._params and isinstance(self["qt"], float):
            self["qt"] = int((time() - self["qt"]) * 1000)
        MPDataPusher().push(self._params)


@util.singleton
class MPDataPusher:

    MAX_WORKERS = 5

    def __init__(self):
        self._queue = queue.LifoQueue()
        self._failedque = deque()
        self._http_session = HTTPSession()
        self._http_offline = False
        self._workers = []

    def push(self, item):
        # if network is off-line
        if self._http_offline:
            if "qt" not in item:
                item["qt"] = time()
            self._failedque.append(item)
            return

        self._queue.put(item)
        self._tune_workers()

    def in_wait(self):
        return self._queue.unfinished_tasks

    def get_items(self):
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
                if self._send_data(item):
                    self._failedque.remove(_item)
                self._queue.task_done()
            except:  # pylint: disable=W0702
                pass

    def _send_data(self, data):
        if self._http_offline:
            return False
        try:
            r = self._http_session.post(
                "https://ssl.google-analytics.com/collect",
                data=data,
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


def on_command():
    resend_backuped_reports()

    mp = MeasurementProtocol()
    mp.send("screenview")

    if is_ci():
        measure_ci()


def on_exception(e):
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
    send_exception(description, is_fatal)


def measure_ci():
    event = {"category": "CI", "action": "NoName", "label": None}
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
            event["action"] = name
            break
    send_event(**event)


def dump_run_environment(options):
    non_sensitive_data = [
        "platform",
        "platform_packages",
        "framework",
        "board",
        "upload_protocol",
        "check_tool",
        "debug_tool",
        "monitor_filters",
        "test_framework",
    ]
    safe_options = {k: v for k, v in options.items() if k in non_sensitive_data}
    if is_platformio_project(os.getcwd()):
        phash = hashlib.sha1(hashlib_encode_data(app.get_cid()))
        safe_options["pid"] = phash.hexdigest()
    return json.dumps(safe_options, sort_keys=True, ensure_ascii=False)


def send_run_environment(options, targets):
    send_event(
        "Env",
        " ".join([t.title() for t in targets or ["run"]]),
        dump_run_environment(options),
    )


def send_event(category, action, label=None, value=None, screen_name=None):
    mp = MeasurementProtocol()
    mp["event_category"] = category[:150]
    mp["event_action"] = action[:500]
    if label:
        mp["event_label"] = label[:500]
    if value:
        mp["event_value"] = int(value)
    if screen_name:
        mp["screen_name"] = screen_name[:2048]
    mp.send("event")


def send_exception(description, is_fatal=False):
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

    mp = MeasurementProtocol()
    mp["exd"] = description[:8192].strip()
    mp["exf"] = 1 if is_fatal else 0
    mp.send("exception")


@atexit.register
def _finalize():
    timeout = 1000  # msec
    elapsed = 0
    try:
        while elapsed < timeout:
            if not MPDataPusher().in_wait():
                break
            sleep(0.2)
            elapsed += 200
        backup_reports(MPDataPusher().get_items())
    except KeyboardInterrupt:
        pass


def backup_reports(items):
    if not items:
        return

    KEEP_MAX_REPORTS = 100
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm:
        tm["backup"] = []

    for params in items:
        # skip static options
        for key in list(params.keys()):
            if key in ("v", "tid", "cid", "cd1", "cd2", "sr", "an"):
                del params[key]

        # store time in UNIX format
        if "qt" not in params:
            params["qt"] = time()
        elif not isinstance(params["qt"], float):
            params["qt"] = time() - (params["qt"] / 1000)

        tm["backup"].append(params)

    tm["backup"] = tm["backup"][KEEP_MAX_REPORTS * -1 :]
    app.set_state_item("telemetry", tm)


def resend_backuped_reports():
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm or not tm["backup"]:
        return False

    for report in tm["backup"]:
        mp = MeasurementProtocol()
        for key, value in report.items():
            mp[key] = value
        mp.send(report["t"])

    # clean
    tm["backup"] = []
    app.set_state_item("telemetry", tm)
    return True
