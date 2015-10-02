# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import platform
import Queue
import re
import sys
import threading
import uuid
from collections import deque
from os import getenv
from time import sleep, time

import click
import requests

from platformio import __version__, app, exception, util
from platformio.ide.projectgenerator import ProjectGenerator


class TelemetryBase(object):

    MACHINE_ID = str(uuid.uuid5(uuid.NAMESPACE_OID, str(uuid.getnode())))

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

    TRACKING_ID = "UA-1768265-9"
    PARAMS_MAP = {
        "screen_name": "cd",
        "event_category": "ec",
        "event_action": "ea",
        "event_label": "el",
        "event_value": "ev"
    }

    def __init__(self):
        TelemetryBase.__init__(self)
        self['v'] = 1
        self['tid'] = self.TRACKING_ID
        self['cid'] = self.MACHINE_ID

        self['sr'] = "%dx%d" % click.get_terminal_size()
        self._prefill_screen_name()
        self._prefill_appinfo()
        self._prefill_custom_data()

    def __getitem__(self, name):
        if name in self.PARAMS_MAP:
            name = self.PARAMS_MAP[name]
        return TelemetryBase.__getitem__(self, name)

    def __setitem__(self, name, value):
        if name in self.PARAMS_MAP:
            name = self.PARAMS_MAP[name]
        TelemetryBase.__setitem__(self, name, value)

    def _prefill_appinfo(self):
        self['av'] = __version__

        # gather dependent packages
        dpdata = []
        dpdata.append("Click/%s" % click.__version__)
        if app.get_session_var("caller_id"):
            dpdata.append("Caller/%s" % app.get_session_var("caller_id"))
        try:
            result = util.exec_command(["scons", "--version"])
            match = re.search(r"engine: v([\d\.]+)", result['out'])
            if match:
                dpdata.append("SCons/%s" % match.group(1))
        except:  # pylint: disable=W0702
            pass
        self['an'] = " ".join(dpdata)

    def _prefill_custom_data(self):
        self['cd1'] = util.get_systype()
        self['cd2'] = "Python/%s %s" % (platform.python_version(),
                                        platform.platform())
        self['cd4'] = (1 if app.get_setting("enable_prompts") or
                       app.get_session_var("caller_id") else 0)

    def _prefill_screen_name(self):
        self['cd3'] = " ".join([str(s).lower() for s in sys.argv[1:]])

        if not app.get_session_var("command_ctx"):
            return
        ctx_args = app.get_session_var("command_ctx").args
        args = [str(s).lower() for s in ctx_args if not str(s).startswith("-")]
        if not args:
            return
        if args[0] in ("lib", "platforms", "serialports", "settings"):
            cmd_path = args[:2]
        else:
            cmd_path = args[:1]
        self['screen_name'] = " ".join([p.title() for p in cmd_path])

    def send(self, hittype):
        if not app.get_setting("enable_telemetry"):
            return

        self['t'] = hittype

        # correct queue time
        if "qt" in self._params and isinstance(self['qt'], float):
            self['qt'] = int((time() - self['qt']) * 1000)

        MPDataPusher().push(self._params)


@util.singleton
class MPDataPusher(object):

    MAX_WORKERS = 5

    def __init__(self):
        self._queue = Queue.LifoQueue()
        self._failedque = deque()
        self._http_session = requests.Session()
        self._http_offline = False
        self._workers = []

    def push(self, item):
        # if network is off-line
        if self._http_offline:
            if "qt" not in item:
                item['qt'] = time()
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
        except Queue.Empty:
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
            item = self._queue.get()
            _item = item.copy()
            if "qt" not in _item:
                _item['qt'] = time()
            self._failedque.append(_item)
            if self._send_data(item):
                self._failedque.remove(_item)
            else:
                self._http_offline = True
            self._queue.task_done()

    def _send_data(self, data):
        result = False
        try:
            r = self._http_session.post(
                "https://ssl.google-analytics.com/collect",
                data=data,
                headers=util.get_request_defheaders(),
                timeout=2
            )
            r.raise_for_status()
            result = True
        except:  # pylint: disable=W0702
            pass
        return result


def on_command():
    resend_backuped_reports()

    mp = MeasurementProtocol()
    mp.send("screenview")

    if util.is_ci():
        measure_ci()

    if app.get_session_var("caller_id"):
        measure_caller(app.get_session_var("caller_id"))


def measure_ci():
    event = {
        "category": "CI",
        "action": "NoName",
        "label": None
    }

    envmap = {
        "APPVEYOR": {"label": getenv("APPVEYOR_REPO_NAME")},
        "CIRCLECI": {"label": "%s/%s" % (getenv("CIRCLE_PROJECT_USERNAME"),
                                         getenv("CIRCLE_PROJECT_REPONAME"))},
        "TRAVIS": {"label": getenv("TRAVIS_REPO_SLUG")},
        "SHIPPABLE": {"label": getenv("REPO_NAME")},
        "DRONE": {"label": getenv("DRONE_REPO_SLUG")}
    }

    for key, value in envmap.iteritems():
        if getenv(key, "").lower() != "true":
            continue
        event.update({"action": key, "label": value['label']})

    on_event(**event)


def measure_caller(calller_id):
    calller_id = str(calller_id)[:20].lower()
    event = {
        "category": "Caller",
        "action": "Misc",
        "label": calller_id
    }
    if calller_id in (["atom", "vim"] + ProjectGenerator.get_supported_ides()):
        event['action'] = "IDE"
    on_event(**event)


def on_run_environment(options, targets):
    opts = ["%s=%s" % (opt, value) for opt, value in sorted(options.items())]
    targets = [t.title() for t in targets or ["run"]]
    on_event("Env", " ".join(targets), "&".join(opts))


def on_event(category, action, label=None, value=None, screen_name=None):
    mp = MeasurementProtocol()
    mp['event_category'] = category[:150]
    mp['event_action'] = action[:500]
    if label:
        mp['event_label'] = label[:500]
    if value:
        mp['event_value'] = int(value)
    if screen_name:
        mp['screen_name'] = screen_name[:2048]
    mp.send("event")


def on_exception(e):
    if isinstance(e, exception.AbortedByUser):
        return
    mp = MeasurementProtocol()
    mp['exd'] = "%s: %s" % (type(e).__name__, e)
    mp['exf'] = int(not isinstance(e, exception.PlatformioException))
    mp.send("exception")


@atexit.register
def _finalize():
    timeout = 1000  # msec
    elapsed = 0
    while elapsed < timeout:
        if not MPDataPusher().in_wait():
            break
        sleep(0.2)
        elapsed += 200
    backup_reports(MPDataPusher().get_items())


def backup_reports(items):
    if not items:
        return

    KEEP_MAX_REPORTS = 100
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm:
        tm['backup'] = []

    for params in items:
        # skip static options
        for key in params.keys():
            if key in ("v", "tid", "cid", "cd1", "cd2", "sr", "an"):
                del params[key]

        # store time in UNIX format
        if "qt" not in params:
            params['qt'] = time()
        elif not isinstance(params['qt'], float):
            params['qt'] = time() - (params['qt'] / 1000)

        tm['backup'].append(params)

    tm['backup'] = tm['backup'][KEEP_MAX_REPORTS * -1:]
    app.set_state_item("telemetry", tm)


def resend_backuped_reports():
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm or not tm['backup']:
        return False

    for report in tm['backup']:
        mp = MeasurementProtocol()
        for key, value in report.items():
            mp[key] = value
        mp.send(report['t'])

    # clean
    tm['backup'] = []
    app.set_state_item("telemetry", tm)
