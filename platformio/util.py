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

import json
import math
import os
import platform
import re
import shutil
import time
from functools import wraps
from glob import glob

import click
import zeroconf

from platformio import __version__, exception, proc
from platformio.compat import IS_MACOS, IS_WINDOWS
from platformio.fs import cd, load_json  # pylint: disable=unused-import
from platformio.proc import exec_command  # pylint: disable=unused-import


class memoized(object):
    def __init__(self, expire=0):
        expire = str(expire)
        if expire.isdigit():
            expire = "%ss" % int((int(expire) / 1000))
        tdmap = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        assert expire.endswith(tuple(tdmap))
        self.expire = int(tdmap[expire[-1]] * int(expire[:-1]))
        self.cache = {}

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key not in self.cache or (
                self.expire > 0 and self.cache[key][0] < time.time() - self.expire
            ):
                self.cache[key] = (time.time(), func(*args, **kwargs))
            return self.cache[key][1]

        wrapper.reset = self._reset
        return wrapper

    def _reset(self):
        self.cache.clear()


class throttle(object):
    def __init__(self, threshhold):
        self.threshhold = threshhold  # milliseconds
        self.last = 0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            diff = int(round((time.time() - self.last) * 1000))
            if diff < self.threshhold:
                time.sleep((self.threshhold - diff) * 0.001)
            self.last = time.time()
            return func(*args, **kwargs)

        return wrapper


def singleton(cls):
    """From PEP-318 http://www.python.org/dev/peps/pep-0318/#examples"""
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


def get_systype():
    type_ = platform.system().lower()
    arch = platform.machine().lower()
    if type_ == "windows":
        arch = "amd64" if platform.architecture()[0] == "64bit" else "x86"
    return "%s_%s" % (type_, arch) if arch else type_


def get_serial_ports(filter_hwid=False):
    try:
        # pylint: disable=import-outside-toplevel
        from serial.tools.list_ports import comports
    except ImportError:
        raise exception.GetSerialPortsError(os.name)

    result = []
    for p, d, h in comports():
        if not p:
            continue
        if not filter_hwid or "VID:PID" in h:
            result.append({"port": p, "description": d, "hwid": h})

    if filter_hwid:
        return result

    # fix for PySerial
    if not result and IS_MACOS:
        for p in glob("/dev/tty.*"):
            result.append({"port": p, "description": "n/a", "hwid": "n/a"})
    return result


# Backward compatibility for PIO Core <3.5
get_serialports = get_serial_ports


def get_logical_devices():
    items = []
    if IS_WINDOWS:
        try:
            result = proc.exec_command(
                ["wmic", "logicaldisk", "get", "name,VolumeName"]
            ).get("out", "")
            devicenamere = re.compile(r"^([A-Z]{1}\:)\s*(\S+)?")
            for line in result.split("\n"):
                match = devicenamere.match(line.strip())
                if not match:
                    continue
                items.append({"path": match.group(1) + "\\", "name": match.group(2)})
            return items
        except WindowsError:  # pylint: disable=undefined-variable
            pass
        # try "fsutil"
        result = proc.exec_command(["fsutil", "fsinfo", "drives"]).get("out", "")
        for device in re.findall(r"[A-Z]:\\", result):
            items.append({"path": device, "name": None})
        return items

    result = proc.exec_command(["df"]).get("out")
    devicenamere = re.compile(r"^/.+\d+\%\s+([a-z\d\-_/]+)$", flags=re.I)
    for line in result.split("\n"):
        match = devicenamere.match(line.strip())
        if not match:
            continue
        items.append({"path": match.group(1), "name": os.path.basename(match.group(1))})
    return items


def get_mdns_services():
    class mDNSListener(object):
        def __init__(self):
            self._zc = zeroconf.Zeroconf(interfaces=zeroconf.InterfaceChoice.All)
            self._found_types = []
            self._found_services = []

        def __enter__(self):
            zeroconf.ServiceBrowser(
                self._zc,
                [
                    "_http._tcp.local.",
                    "_hap._tcp.local.",
                    "_services._dns-sd._udp.local.",
                ],
                self,
            )
            return self

        def __exit__(self, etype, value, traceback):
            self._zc.close()

        def add_service(self, zc, type_, name):
            try:
                assert zeroconf.service_type_name(name)
                assert str(name)
            except (AssertionError, UnicodeError, zeroconf.BadTypeInNameException):
                return
            if name not in self._found_types:
                self._found_types.append(name)
                zeroconf.ServiceBrowser(self._zc, name, self)
            if type_ in self._found_types:
                s = zc.get_service_info(type_, name)
                if s:
                    self._found_services.append(s)

        def remove_service(self, zc, type_, name):
            pass

        def update_service(self, zc, type_, name):
            pass

        def get_services(self):
            return self._found_services

    items = []
    with mDNSListener() as mdns:
        time.sleep(3)
        for service in mdns.get_services():
            properties = None
            if service.properties:
                try:
                    properties = {
                        k.decode("utf8"): v.decode("utf8")
                        if isinstance(v, bytes)
                        else v
                        for k, v in service.properties.items()
                    }
                    json.dumps(properties)
                except UnicodeDecodeError:
                    properties = None

            items.append(
                {
                    "type": service.type,
                    "name": service.name,
                    "ip": ", ".join(service.parsed_addresses()),
                    "port": service.port,
                    "properties": properties,
                }
            )
    return items


def pioversion_to_intstr():
    """Legacy for  framework-zephyr/scripts/platformio/platformio-build-pre.py"""
    vermatch = re.match(r"^([\d\.]+)", __version__)
    assert vermatch
    return [int(i) for i in vermatch.group(1).split(".")[:3]]


def items_to_list(items):
    if isinstance(items, list):
        return items
    return [i.strip() for i in items.split(",") if i.strip()]


def items_in_list(needle, haystack):
    needle = items_to_list(needle)
    haystack = items_to_list(haystack)
    if "*" in needle or "*" in haystack:
        return True
    return set(needle) & set(haystack)


def parse_date(datestr):
    if "T" in datestr and "Z" in datestr:
        return time.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
    return time.strptime(datestr)


def merge_dicts(d1, d2, path=None):
    if path is None:
        path = []
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key], path + [str(key)])
        else:
            d1[key] = d2[key]
    return d1


def print_labeled_bar(label, is_error=False, fg=None):
    terminal_width, _ = shutil.get_terminal_size()
    width = len(click.unstyle(label))
    half_line = "=" * int((terminal_width - width - 2) / 2)
    click.secho("%s %s %s" % (half_line, label, half_line), fg=fg, err=is_error)


def humanize_duration_time(duration):
    if duration is None:
        return duration
    duration = duration * 1000
    tokens = []
    for multiplier in (3600000, 60000, 1000, 1):
        fraction = math.floor(duration / multiplier)
        tokens.append(int(round(duration) if multiplier == 1 else fraction))
        duration -= fraction * multiplier
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(*tokens)
