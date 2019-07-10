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
import os
import platform
import re
import socket
import stat
import sys
import time
from contextlib import contextmanager
from functools import wraps
from glob import glob
from os.path import abspath, basename, dirname, isfile, join
from shutil import rmtree

import click
import requests

from platformio import __apiurl__, __version__, exception
from platformio.commands import PlatformioCLI
from platformio.compat import PY2, WINDOWS, get_file_contents
from platformio.proc import exec_command, is_ci


class cd(object):

    def __init__(self, new_path):
        self.new_path = new_path
        self.prev_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.prev_path)


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
            if (key not in self.cache
                    or (self.expire > 0
                        and self.cache[key][0] < time.time() - self.expire)):
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


def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except ValueError:
        raise exception.InvalidJSONFile(file_path)


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


def get_source_dir():
    curpath = abspath(__file__)
    if not isfile(curpath):
        for p in sys.path:
            if isfile(join(p, __file__)):
                curpath = join(p, __file__)
                break
    return dirname(curpath)


def change_filemtime(path, mtime):
    os.utime(path, (mtime, mtime))


def get_serial_ports(filter_hwid=False):
    try:
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
                ["wmic", "logicaldisk", "get",
                 "name,VolumeName"]).get("out", "")
            devicenamere = re.compile(r"^([A-Z]{1}\:)\s*(\S+)?")
            for line in result.split("\n"):
                match = devicenamere.match(line.strip())
                if not match:
                    continue
                items.append({
                    "path": match.group(1) + "\\",
                    "name": match.group(2)
                })
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
        items.append({
            "path": match.group(1),
            "name": basename(match.group(1))
        })
    return items


def get_mdns_services():
    try:
        import zeroconf
    except ImportError:
        from site import addsitedir
        from platformio.managers.core import get_core_package_dir
        contrib_pysite_dir = get_core_package_dir("contrib-pysite")
        addsitedir(contrib_pysite_dir)
        sys.path.insert(0, contrib_pysite_dir)
        import zeroconf

    class mDNSListener(object):

        def __init__(self):
            self._zc = zeroconf.Zeroconf(
                interfaces=zeroconf.InterfaceChoice.All)
            self._found_types = []
            self._found_services = []

        def __enter__(self):
            zeroconf.ServiceBrowser(self._zc, "_services._dns-sd._udp.local.",
                                    self)
            return self

        def __exit__(self, etype, value, traceback):
            self._zc.close()

        def remove_service(self, zc, type_, name):
            pass

        def add_service(self, zc, type_, name):
            try:
                assert zeroconf.service_type_name(name)
                assert str(name)
            except (AssertionError, UnicodeError,
                    zeroconf.BadTypeInNameException):
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
                        k.decode("utf8"):
                        v.decode("utf8") if isinstance(v, bytes) else v
                        for k, v in service.properties.items()
                    }
                    json.dumps(properties)
                except UnicodeDecodeError:
                    properties = None

            items.append({
                "type":
                service.type,
                "name":
                service.name,
                "ip":
                ".".join([
                    str(c if isinstance(c, int) else ord(c))
                    for c in service.address
                ]),
                "port":
                service.port,
                "properties":
                properties
            })
    return items


def get_request_defheaders():
    data = (__version__, int(is_ci()), requests.utils.default_user_agent())
    return {"User-Agent": "PlatformIO/%s CI/%d %s" % data}


@memoized(expire="60s")
def _api_request_session():
    return requests.Session()


@throttle(500)
def _get_api_result(
        url,  # pylint: disable=too-many-branches
        params=None,
        data=None,
        auth=None):
    from platformio.app import get_setting

    result = {}
    r = None
    verify_ssl = sys.version_info >= (2, 7, 9)

    headers = get_request_defheaders()
    if not url.startswith("http"):
        url = __apiurl__ + url
        if not get_setting("enable_ssl"):
            url = url.replace("https://", "http://")

    try:
        if data:
            r = _api_request_session().post(url,
                                            params=params,
                                            data=data,
                                            headers=headers,
                                            auth=auth,
                                            verify=verify_ssl)
        else:
            r = _api_request_session().get(url,
                                           params=params,
                                           headers=headers,
                                           auth=auth,
                                           verify=verify_ssl)
        result = r.json()
        r.raise_for_status()
        return r.text
    except requests.exceptions.HTTPError as e:
        if result and "message" in result:
            raise exception.APIRequestError(result['message'])
        if result and "errors" in result:
            raise exception.APIRequestError(result['errors'][0]['title'])
        raise exception.APIRequestError(e)
    except ValueError:
        raise exception.APIRequestError("Invalid response: %s" %
                                        r.text.encode("utf-8"))
    finally:
        if r:
            r.close()
    return None


def get_api_result(url, params=None, data=None, auth=None, cache_valid=None):
    from platformio.app import ContentCache
    total = 0
    max_retries = 5
    cache_key = (ContentCache.key_from_args(url, params, data, auth)
                 if cache_valid else None)
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
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            total += 1
            if not PlatformioCLI.in_silence():
                click.secho(
                    "[API] ConnectionError: {0} (incremented retry: max={1}, "
                    "total={2})".format(e, max_retries, total),
                    fg="yellow")
            time.sleep(2 * total)

    raise exception.APIRequestError(
        "Could not connect to PlatformIO API Service. "
        "Please try later.")


PING_INTERNET_IPS = [
    "192.30.253.113",  # github.com
    "193.222.52.25"  # dl.platformio.org
]


@memoized(expire="5s")
def _internet_on():
    timeout = 2
    socket.setdefaulttimeout(timeout)
    for ip in PING_INTERNET_IPS:
        try:
            if os.getenv("HTTP_PROXY", os.getenv("HTTPS_PROXY")):
                requests.get("http://%s" % ip,
                             allow_redirects=False,
                             timeout=timeout)
            else:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                    (ip, 80))
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
    if not isinstance(items, list):
        items = [i.strip() for i in items.split(",")]
    return [i.lower() for i in items if i]


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


def format_filesize(filesize):
    base = 1024
    unit = 0
    suffix = "B"
    filesize = float(filesize)
    if filesize < base:
        return "%d%s" % (filesize, suffix)
    for i, suffix in enumerate("KMGTPEZY"):
        unit = base**(i + 2)
        if filesize >= unit:
            continue
        if filesize % (base**(i + 1)):
            return "%.2f%sB" % ((base * filesize / unit), suffix)
        break
    return "%d%sB" % ((base * filesize / unit), suffix)


def merge_dicts(d1, d2, path=None):
    if path is None:
        path = []
    for key in d2:
        if (key in d1 and isinstance(d1[key], dict)
                and isinstance(d2[key], dict)):
            merge_dicts(d1[key], d2[key], path + [str(key)])
        else:
            d1[key] = d2[key]
    return d1


def ensure_udev_rules():

    def _rules_to_set(rules_path):
        return set(l.strip() for l in get_file_contents(rules_path).split("\n")
                   if l.strip() and not l.startswith("#"))

    if "linux" not in get_systype():
        return None
    installed_rules = [
        "/etc/udev/rules.d/99-platformio-udev.rules",
        "/lib/udev/rules.d/99-platformio-udev.rules"
    ]
    if not any(isfile(p) for p in installed_rules):
        raise exception.MissedUdevRules

    origin_path = abspath(
        join(get_source_dir(), "..", "scripts", "99-platformio-udev.rules"))
    if not isfile(origin_path):
        return None

    origin_rules = _rules_to_set(origin_path)
    for rules_path in installed_rules:
        if not isfile(rules_path):
            continue
        current_rules = _rules_to_set(rules_path)
        if not origin_rules <= current_rules:
            raise exception.OutdatedUdevRules(rules_path)

    return True


def get_original_version(version):
    if version.count(".") != 2:
        return None
    _, raw = version.split(".")[:2]
    if int(raw) <= 99:
        return None
    if int(raw) <= 9999:
        return "%s.%s" % (raw[:-2], int(raw[-2:]))
    return "%s.%s.%s" % (raw[:-4], int(raw[-4:-2]), int(raw[-2:]))


def rmtree_(path):

    def _onerror(_, name, __):
        try:
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)
        except Exception as e:  # pylint: disable=broad-except
            click.secho("%s \nPlease manually remove the file `%s`" %
                        (str(e), name),
                        fg="red",
                        err=True)

    return rmtree(path, onerror=_onerror)
