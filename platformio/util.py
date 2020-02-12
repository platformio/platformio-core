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

import json
import math
import os
import platform
import re
import socket
import sys
import time
from contextlib import contextmanager
from functools import wraps
from glob import glob

import click
import requests

from platformio import __apiurl__, __version__, exception
from platformio.commands import PlatformioCLI
from platformio.compat import PY2, WINDOWS
from platformio.fs import cd  # pylint: disable=unused-import
from platformio.fs import load_json  # pylint: disable=unused-import
from platformio.fs import rmtree as rmtree_  # pylint: disable=unused-import
from platformio.proc import exec_command  # pylint: disable=unused-import
from platformio.proc import is_ci  # pylint: disable=unused-import

# KEEP unused imports for backward compatibility with PIO Core 3.0 API


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
    """ From PEP-318 http://www.python.org/dev/peps/pep-0318/#examples """
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


@contextmanager
def capture_std_streams(stdout, stderr=None):
    _stdout = sys.stdout
    _stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr or stdout
    yield
    sys.stdout = _stdout
    sys.stderr = _stderr


def get_systype():
    type_ = platform.system().lower()
    arch = platform.machine().lower()
    if type_ == "windows":
        arch = "amd64" if platform.architecture()[0] == "64bit" else "x86"
    return "%s_%s" % (type_, arch) if arch else type_


def pioversion_to_intstr():
    vermatch = re.match(r"^([\d\.]+)", __version__)
    assert vermatch
    return [int(i) for i in vermatch.group(1).split(".")[:3]]


def change_filemtime(path, mtime):
    os.utime(path, (mtime, mtime))


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
        if WINDOWS and PY2:
            try:
                # pylint: disable=undefined-variable
                d = unicode(d, errors="ignore")
            except TypeError:
                pass
        if not filter_hwid or "VID:PID" in h:
            result.append({"port": p, "description": d, "hwid": h})

    if filter_hwid:
        return result

    # fix for PySerial
    if not result and "darwin" in get_systype():
        for p in glob("/dev/tty.*"):
            result.append({"port": p, "description": "n/a", "hwid": "n/a"})
    return result


# Backward compatibility for PIO Core <3.5
get_serialports = get_serial_ports


def get_logical_devices():
    items = []
    if WINDOWS:
        try:
            result = exec_command(
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
        result = exec_command(["fsutil", "fsinfo", "drives"]).get("out", "")
        for device in re.findall(r"[A-Z]:\\", result):
            items.append({"path": device, "name": None})
        return items

    result = exec_command(["df"]).get("out")
    devicenamere = re.compile(r"^/.+\d+\%\s+([a-z\d\-_/]+)$", flags=re.I)
    for line in result.split("\n"):
        match = devicenamere.match(line.strip())
        if not match:
            continue
        items.append({"path": match.group(1), "name": os.path.basename(match.group(1))})
    return items


def get_mdns_services():
    # pylint: disable=import-outside-toplevel
    try:
        import zeroconf
    except ImportError:
        from site import addsitedir
        from platformio.managers.core import get_core_package_dir

        contrib_pysite_dir = get_core_package_dir("contrib-pysite")
        addsitedir(contrib_pysite_dir)
        sys.path.insert(0, contrib_pysite_dir)
        import zeroconf  # pylint: disable=import-outside-toplevel

    class mDNSListener(object):
        def __init__(self):
            self._zc = zeroconf.Zeroconf(interfaces=zeroconf.InterfaceChoice.All)
            self._found_types = []
            self._found_services = []

        def __enter__(self):
            zeroconf.ServiceBrowser(self._zc, "_services._dns-sd._udp.local.", self)
            return self

        def __exit__(self, etype, value, traceback):
            self._zc.close()

        def remove_service(self, zc, type_, name):
            pass

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
                    "ip": ".".join(
                        [
                            str(c if isinstance(c, int) else ord(c))
                            for c in service.address
                        ]
                    ),
                    "port": service.port,
                    "properties": properties,
                }
            )
    return items


def get_request_defheaders():
    data = (__version__, int(is_ci()), requests.utils.default_user_agent())
    return {"User-Agent": "PlatformIO/%s CI/%d %s" % data}


@memoized(expire="60s")
def _api_request_session():
    return requests.Session()


@throttle(500)
def _get_api_result(
    url, params=None, data=None, auth=None  # pylint: disable=too-many-branches
):
    from platformio.app import get_setting  # pylint: disable=import-outside-toplevel

    result = {}
    r = None
    verify_ssl = sys.version_info >= (2, 7, 9)

    headers = get_request_defheaders()
    if not url.startswith("http"):
        url = __apiurl__ + url
        if not get_setting("strict_ssl"):
            url = url.replace("https://", "http://")

    try:
        if data:
            r = _api_request_session().post(
                url,
                params=params,
                data=data,
                headers=headers,
                auth=auth,
                verify=verify_ssl,
            )
        else:
            r = _api_request_session().get(
                url, params=params, headers=headers, auth=auth, verify=verify_ssl
            )
        result = r.json()
        r.raise_for_status()
        return r.text
    except requests.exceptions.HTTPError as e:
        if result and "message" in result:
            raise exception.APIRequestError(result["message"])
        if result and "errors" in result:
            raise exception.APIRequestError(result["errors"][0]["title"])
        raise exception.APIRequestError(e)
    except ValueError:
        raise exception.APIRequestError("Invalid response: %s" % r.text.encode("utf-8"))
    finally:
        if r:
            r.close()
    return None


def get_api_result(url, params=None, data=None, auth=None, cache_valid=None):
    from platformio.app import ContentCache  # pylint: disable=import-outside-toplevel

    total = 0
    max_retries = 5
    cache_key = (
        ContentCache.key_from_args(url, params, data, auth) if cache_valid else None
    )
    while total < max_retries:
        try:
            with ContentCache() as cc:
                if cache_key:
                    result = cc.get(cache_key)
                    if result is not None:
                        return json.loads(result)

            # check internet before and resolve issue with 60 seconds timeout
            internet_on(raise_exception=True)

            result = _get_api_result(url, params, data)
            if cache_valid:
                with ContentCache() as cc:
                    cc.set(cache_key, result, cache_valid)
            return json.loads(result)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            total += 1
            if not PlatformioCLI.in_silence():
                click.secho(
                    "[API] ConnectionError: {0} (incremented retry: max={1}, "
                    "total={2})".format(e, max_retries, total),
                    fg="yellow",
                )
            time.sleep(2 * total)

    raise exception.APIRequestError(
        "Could not connect to PlatformIO API Service. Please try later."
    )


PING_REMOTE_HOSTS = [
    "140.82.118.3",  # Github.com
    "35.231.145.151",  # Gitlab.com
    "github.com",
    "platformio.org",
]


@memoized(expire="5s")
def _internet_on():
    timeout = 2
    socket.setdefaulttimeout(timeout)
    for host in PING_REMOTE_HOSTS:
        try:
            if os.getenv("HTTP_PROXY", os.getenv("HTTPS_PROXY")):
                requests.get("http://%s" % host, allow_redirects=False, timeout=timeout)
            else:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 80))
            return True
        except:  # pylint: disable=bare-except
            pass
    return False


def internet_on(raise_exception=False):
    result = _internet_on()
    if raise_exception and not result:
        raise exception.InternetIsOffline()
    return result


def pepver_to_semver(pepver):
    return re.sub(r"(\.\d+)\.?(dev|a|b|rc|post)", r"\1-\2.", pepver, 1)


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
    terminal_width, _ = click.get_terminal_size()
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


def get_original_version(version):
    if version.count(".") != 2:
        return None
    _, raw = version.split(".")[:2]
    if int(raw) <= 99:
        return None
    if int(raw) <= 9999:
        return "%s.%s" % (raw[:-2], int(raw[-2:]))
    return "%s.%s.%s" % (raw[:-4], int(raw[-4:-2]), int(raw[-2:]))
