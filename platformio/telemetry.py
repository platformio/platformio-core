# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import platform
import re
import uuid
from sys import argv as sys_argv
from time import time

import click
import requests

from platformio import __version__, app
from platformio.util import exec_command, get_systype


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

    @classmethod
    def session_instance(cls):
        try:
            return cls._session_instance
        except AttributeError:
            cls._session_instance = requests.Session()
        return cls._session_instance

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
            result = exec_command(["scons", "--version"])
            match = re.search(r"engine: v([\d\.]+)", result['out'])
            if match:
                dpdata.append("SCons/%s" % match.group(1))
        except:  # pylint: disable=W0702
            pass
        self['an'] = " ".join(dpdata)

    def _prefill_custom_data(self):
        self['cd1'] = get_systype()
        self['cd2'] = "Python/%s %s" % (platform.python_version(),
                                        platform.platform())

    def _prefill_screen_name(self):
        args = [str(s).lower() for s in sys_argv[1:]]
        if not args:
            return

        if args[0] in ("lib", "settings"):
            cmd_path = args[:2]
        else:
            cmd_path = args[:1]

        self['screen_name'] = " ".join([p.title() for p in cmd_path])
        self['cd3'] = " ".join(args)

    def send(self, hittype):
        self['t'] = hittype

        # correct queue time
        if "qt" in self._params and isinstance(self['qt'], float):
            self['qt'] = int((time() - self['qt']) * 1000)

        try:
            r = self.session_instance().post(
                "https://ssl.google-analytics.com/collect",
                data=self._params
            )
            r.raise_for_status()
        except:  # pylint: disable=W0702
            backup_report(self._params)
            return False
        return True


def on_command(ctx):  # pylint: disable=W0613
    mp = MeasurementProtocol()
    if mp.send("screenview"):
        resend_backuped_reports()


def on_run_environment(name, options):  # pylint: disable=W0613
    # on_event("RunEnv", "Name", name)
    for opt, value in options:
        on_event("RunEnv", opt.title(), value)


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
    return mp.send("event")


def on_exception(e):
    mp = MeasurementProtocol()
    mp['exd'] = "%s: %s" % (type(e).__name__, e)
    mp['exf'] = 1
    return mp.send("exception")


def backup_report(params):
    KEEP_MAX_REPORTS = 1000
    tm = app.get_state_item("telemetry", {})
    if "backup" not in tm:
        tm['backup'] = []

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


def resend_backuped_reports():
    MAX_RESEND_REPORTS = 10

    resent_nums = 0
    while resent_nums < MAX_RESEND_REPORTS:
        tm = app.get_state_item("telemetry", {})
        if "backup" not in tm or not tm['backup']:
            break

        report = tm['backup'].pop()
        app.set_state_item("telemetry", tm)
        resent_nums += 1

        mp = MeasurementProtocol()
        for key, value in report.items():
            mp[key] = value
        if not mp.send(report['t']):
            break
