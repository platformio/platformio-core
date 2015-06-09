# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import platform
import re
import sys
import threading
import uuid
from time import time

import click
import requests

from platformio import __version__, app, exception, util


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
        # dpdata.append("Requests/%s" % requests.__version__)
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
        self['cd4'] = 1 if app.get_setting("enable_prompts") else 0

    def _prefill_screen_name(self):
        args = [str(s).lower() for s in sys.argv[1:]
                if not str(s).startswith("-")]
        if not args:
            return

        if args[0] in ("lib", "platforms", "serialports", "settings"):
            cmd_path = args[:2]
        else:
            cmd_path = args[:1]

        self['screen_name'] = " ".join([p.title() for p in cmd_path])
        self['cd3'] = " ".join([str(s).lower() for s in sys.argv[1:]])

    def send(self, hittype):
        if not app.get_setting("enable_telemetry"):
            return

        self['t'] = hittype

        # correct queue time
        if "qt" in self._params and isinstance(self['qt'], float):
            self['qt'] = int((time() - self['qt']) * 1000)

        MPDataPusher.get_instance().push(self._params)


class MPDataPusher(threading.Thread):

    @classmethod
    def get_instance(cls):
        try:
            return cls._thinstance
        except AttributeError:
            cls._event = threading.Event()
            cls._thinstance = cls()
            cls._thinstance.start()
        return cls._thinstance

    @classmethod
    def http_session(cls):
        try:
            return cls._http_session
        except AttributeError:
            cls._http_session = requests.Session()
        return cls._http_session

    def __init__(self):
        threading.Thread.__init__(self)
        self._terminate = False
        self._server_online = False
        self._stack = []

    def run(self):
        while not self._terminate:
            self._event.wait()
            if self._terminate or not self._stack:
                return
            self._event.clear()

            data = self._stack.pop()
            try:
                r = self.http_session().post(
                    "https://ssl.google-analytics.com/collect",
                    data=data,
                    headers=util.get_request_defheaders(),
                    timeout=3
                )
                r.raise_for_status()
                self._server_online = True
            except:  # pylint: disable=W0702
                self._server_online = False
                self._stack.append(data)

    def push(self, data):
        self._stack.append(data)
        self._event.set()

    def is_server_online(self):
        return self._server_online

    def get_stack_data(self):
        return self._stack

    def join(self, timeout=0.1):
        self._terminate = True
        self._event.set()
        self.http_session().close()
        threading.Thread.join(self, timeout)


@atexit.register
def _finalize():
    MAX_RESEND_REPORTS = 10
    mpdp = MPDataPusher.get_instance()
    backup_reports(mpdp.get_stack_data())

    resent_nums = 0
    while mpdp.is_server_online() and resent_nums < MAX_RESEND_REPORTS:
        if not resend_backuped_report():
            break
        resent_nums += 1


def on_command(ctx):  # pylint: disable=W0613
    mp = MeasurementProtocol()
    mp.send("screenview")


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


def backup_reports(data):
    if not data:
        return

    KEEP_MAX_REPORTS = 1000
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm:
        tm['backup'] = []

    for params in data:
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

    tm['backup'] = tm['backup'][KEEP_MAX_REPORTS*-1:]
    app.set_state_item("telemetry", tm)


def resend_backuped_report():
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm or not tm['backup']:
        return False

    report = tm['backup'].pop()
    app.set_state_item("telemetry", tm)

    mp = MeasurementProtocol()
    for key, value in report.items():
        mp[key] = value
    mp.send(report['t'])

    return True
