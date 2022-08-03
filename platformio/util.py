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

import functools
import math
import platform
import re
import shutil
import time
from datetime import datetime

import click

from platformio import __version__

# pylint: disable=unused-import
from platformio.device.list.util import list_serial_ports as get_serial_ports
from platformio.fs import cd, load_json
from platformio.proc import exec_command

# pylint: enable=unused-import

# also export list_serial_ports as get_serialports to be
# backward compatibility with arduinosam versions 3.9.0 to 3.5.0 (and possibly others)
get_serialports = get_serial_ports


class memoized:
    def __init__(self, expire=0):
        expire = str(expire)
        if expire.isdigit():
            expire = "%ss" % int((int(expire) / 1000))
        tdmap = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        assert expire.endswith(tuple(tdmap))
        self.expire = int(tdmap[expire[-1]] * int(expire[:-1]))
        self.cache = {}

    def __call__(self, func):
        @functools.wraps(func)
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


class throttle:
    def __init__(self, threshhold):
        self.threshhold = threshhold  # milliseconds
        self.last = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            diff = int(round((time.time() - self.last) * 1000))
            if diff < self.threshhold:
                time.sleep((self.threshhold - diff) * 0.001)
            self.last = time.time()
            return func(*args, **kwargs)

        return wrapper


# Retry: Begin


class RetryException(Exception):
    pass


class RetryNextException(RetryException):
    pass


class RetryStopException(RetryException):
    pass


class retry:

    RetryNextException = RetryNextException
    RetryStopException = RetryStopException

    def __init__(self, timeout=0, step=0.25):
        self.timeout = timeout
        self.step = step

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except self.RetryNextException:
                    pass
                if elapsed >= self.timeout:
                    raise self.RetryStopException()
                elapsed += self.step
                time.sleep(self.step)

        return wrapper


# Retry: End


def singleton(cls):
    """From PEP-318 http://www.python.org/dev/peps/pep-0318/#examples"""
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


def get_systype():
    system = platform.system().lower()
    arch = platform.machine().lower()
    if system == "windows":
        if not arch:  # issue #4353
            arch = "x86_" + platform.architecture()[0]
        if "x86" in arch:
            arch = "amd64" if "64" in arch else "x86"
    return "%s_%s" % (system, arch) if arch else system


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


def parse_datetime(datestr):
    if "T" in datestr and "Z" in datestr:
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.strptime(datestr)


def merge_dicts(d1, d2, path=None):
    if path is None:
        path = []
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key], path + [str(key)])
        else:
            d1[key] = d2[key]
    return d1


def print_labeled_bar(label, is_error=False, fg=None, sep="="):
    terminal_width = shutil.get_terminal_size().columns
    width = len(click.unstyle(label))
    half_line = sep * int((terminal_width - width - 2) / 2)
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


def strip_ansi_codes(text):
    # pylint: disable=protected-access
    return click._compat.strip_ansi(text)
