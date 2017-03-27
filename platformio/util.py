# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import collections
import functools
import json
import os
import platform
import re
import socket
import stat
import subprocess
import sys
from glob import glob
from os.path import (abspath, basename, dirname, expanduser, isdir, isfile,
                     join, normpath, splitdrive)
from shutil import rmtree
from threading import Thread
from time import sleep

import click
import requests

from platformio import __apiurl__, __version__, exception

# pylint: disable=wrong-import-order, too-many-ancestors

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class ProjectConfig(ConfigParser):

    VARTPL_RE = re.compile(r"\$\{([^\.\}]+)\.([^\}]+)\}")

    def items(self, section, **_):
        items = []
        for option in ConfigParser.options(self, section):
            items.append((option, self.get(section, option)))
        return items

    def get(self, section, option, **kwargs):
        value = ConfigParser.get(self, section, option, **kwargs)
        if "${" not in value or "}" not in value:
            return value
        return self.VARTPL_RE.sub(self._re_sub_handler, value)

    def _re_sub_handler(self, match):
        section, option = match.group(1), match.group(2)
        if section == "env" and not self.has_section(section):
            return os.getenv(option)
        return self.get(section, option)


class AsyncPipe(Thread):

    def __init__(self, outcallback=None):
        Thread.__init__(self)
        self.outcallback = outcallback

        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read)
        self._buffer = []

        self.start()

    def get_buffer(self):
        return self._buffer

    def fileno(self):
        return self._fd_write

    def run(self):
        for line in iter(self._pipe_reader.readline, ""):
            line = line.strip()
            self._buffer.append(line)
            if self.outcallback:
                self.outcallback(line)
            else:
                print line
        self._pipe_reader.close()

    def close(self):
        os.close(self._fd_write)
        self.join()


class cd(object):

    def __init__(self, new_path):
        self.new_path = new_path
        self.prev_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.prev_path)


class memoized(object):
    '''
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        fn = functools.partial(self.__call__, obj)
        fn.reset = self._reset
        return fn

    def _reset(self):
        self.cache = {}


def singleton(cls):
    """ From PEP-318 http://www.python.org/dev/peps/pep-0318/#examples """
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except ValueError:
        raise exception.PlatformioException("Could not load broken JSON: %s" %
                                            file_path)


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


def get_project_optional_dir(name, default=None):
    data = None
    var_name = "PLATFORMIO_%s" % name.upper()
    if var_name in os.environ:
        data = os.getenv(var_name)
    else:
        try:
            config = load_project_config()
            if (config.has_section("platformio") and
                    config.has_option("platformio", name)):
                data = config.get("platformio", name)
        except exception.NotPlatformIOProject:
            pass

    if not data:
        return default

    items = []
    for item in data.split(", "):
        if item.startswith("~"):
            item = expanduser(item)
        items.append(abspath(item))
    return ", ".join(items)


def get_home_dir():
    home_dir = get_project_optional_dir("home_dir",
                                        join(expanduser("~"), ".platformio"))

    if "windows" in get_systype():
        try:
            home_dir.encode("utf8")
        except UnicodeDecodeError:
            home_dir = splitdrive(home_dir)[0] + "\\.platformio"

    if not isdir(home_dir):
        os.makedirs(home_dir)

    assert isdir(home_dir)
    return home_dir


def get_source_dir():
    curpath = abspath(__file__)
    if not isfile(curpath):
        for p in sys.path:
            if isfile(join(p, __file__)):
                curpath = join(p, __file__)
                break
    return dirname(curpath)


def get_project_dir():
    return os.getcwd()


def find_project_dir_above(path):
    if isfile(path):
        path = dirname(path)
    if is_platformio_project(path):
        return path
    if isdir(dirname(path)):
        return find_project_dir_above(dirname(path))
    return None


def is_platformio_project(project_dir=None):
    if not project_dir:
        project_dir = get_project_dir()
    return isfile(join(project_dir, "platformio.ini"))


def get_projectlib_dir():
    return get_project_optional_dir("lib_dir", join(get_project_dir(), "lib"))


def get_projectlibdeps_dir():
    return get_project_optional_dir("libdeps_dir",
                                    join(get_project_dir(), ".piolibdeps"))


def get_projectsrc_dir():
    return get_project_optional_dir("src_dir", join(get_project_dir(), "src"))


def get_projecttest_dir():
    return get_project_optional_dir("test_dir",
                                    join(get_project_dir(), "test"))


def get_projectboards_dir():
    return get_project_optional_dir("boards_dir",
                                    join(get_project_dir(), "boards"))


def get_projectpioenvs_dir(force=False):
    path = get_project_optional_dir("envs_dir",
                                    join(get_project_dir(), ".pioenvs"))
    try:
        if not isdir(path):
            os.makedirs(path)
        dontmod_path = join(path, "do-not-modify-files-here.url")
        if not isfile(dontmod_path):
            with open(dontmod_path, "w") as fp:
                fp.write("""
[InternetShortcut]
URL=http://docs.platformio.org/page/projectconf.html#envs-dir
""")
    except Exception as e:  # pylint: disable=broad-except
        if not force:
            raise Exception(e)
    return path


def get_projectdata_dir():
    return get_project_optional_dir("data_dir",
                                    join(get_project_dir(), "data"))


def load_project_config(path=None):
    if not path or isdir(path):
        project_dir = path or get_project_dir()
        if not is_platformio_project(project_dir):
            raise exception.NotPlatformIOProject(project_dir)
        path = join(project_dir, "platformio.ini")
    assert isfile(path)
    cp = ProjectConfig()
    cp.read(path)
    return cp


def change_filemtime(path, time):
    os.utime(path, (time, time))


def is_ci():
    return os.getenv("CI", "").lower() == "true"


def is_container():
    if not isfile("/proc/1/cgroup"):
        return False
    with open("/proc/1/cgroup") as fp:
        for line in fp:
            line = line.strip()
            if ":" in line and not line.endswith(":/"):
                return True
    return False


def exec_command(*args, **kwargs):
    result = {"out": None, "err": None, "returncode": None}

    default = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    default.update(kwargs)
    kwargs = default

    p = subprocess.Popen(*args, **kwargs)
    try:
        result['out'], result['err'] = p.communicate()
        result['returncode'] = p.returncode
    except KeyboardInterrupt:
        raise exception.AbortedByUser()
    finally:
        for s in ("stdout", "stderr"):
            if isinstance(kwargs[s], AsyncPipe):
                kwargs[s].close()

    for s in ("stdout", "stderr"):
        if isinstance(kwargs[s], AsyncPipe):
            result[s[3:]] = "\n".join(kwargs[s].get_buffer())

    for k, v in result.iteritems():
        if v and isinstance(v, basestring):
            result[k].strip()

    return result


def copy_pythonpath_to_osenv():
    _PYTHONPATH = []
    if "PYTHONPATH" in os.environ:
        _PYTHONPATH = os.environ.get("PYTHONPATH").split(os.pathsep)
    for p in os.sys.path:
        conditions = [p not in _PYTHONPATH]
        if "windows" not in get_systype():
            conditions.append(
                isdir(join(p, "click")) or isdir(join(p, "platformio")))
        if all(conditions):
            _PYTHONPATH.append(p)
    os.environ['PYTHONPATH'] = os.pathsep.join(_PYTHONPATH)


def get_serialports(filter_hwid=False):
    try:
        from serial.tools.list_ports import comports
    except ImportError:
        raise exception.GetSerialPortsError(os.name)

    result = []
    for p, d, h in comports():
        if not p:
            continue
        if platform.system() == "Windows":
            try:
                d = unicode(d, errors="ignore")
            except TypeError:
                pass
        if not filter_hwid or "VID:PID" in h:
            result.append({"port": p, "description": d, "hwid": h})

    if filter_hwid:
        return result

    # fix for PySerial
    if not result and platform.system() == "Darwin":
        for p in glob("/dev/tty.*"):
            result.append({"port": p, "description": "n/a", "hwid": "n/a"})
    return result


def get_logicaldisks():
    disks = []
    if platform.system() == "Windows":
        result = exec_command(
            ["wmic", "logicaldisk", "get", "name,VolumeName"]).get("out", "")
        disknamere = re.compile(r"^([A-Z]{1}\:)\s*(\S+)?")
        for line in result.split("\n"):
            match = disknamere.match(line.strip())
            if not match:
                continue
            disks.append({"disk": match.group(1), "name": match.group(2)})
    else:
        result = exec_command(["df"]).get("out")
        disknamere = re.compile(r"\d+\%\s+([a-z\d\-_/]+)$", flags=re.I)
        for line in result.split("\n"):
            match = disknamere.search(line.strip())
            if not match:
                continue
            disks.append({
                "disk": match.group(1),
                "name": basename(match.group(1))
            })
    return disks


def get_request_defheaders():
    data = (__version__, int(is_ci()), requests.utils.default_user_agent())
    return {"User-Agent": "PlatformIO/%s CI/%d %s" % data}


@memoized
def _api_request_session():
    return requests.Session()


def _get_api_result(
        url,  # pylint: disable=too-many-branches
        params=None,
        data=None,
        auth=None):
    from platformio.app import get_setting

    result = None
    r = None
    disable_ssl_check = sys.version_info < (2, 7, 9)

    headers = get_request_defheaders()
    if not url.startswith("http"):
        url = __apiurl__ + url
        if not get_setting("enable_ssl"):
            url = url.replace("https://", "http://")

    try:
        if data:
            r = _api_request_session().post(
                url,
                params=params,
                data=data,
                headers=headers,
                auth=auth,
                verify=disable_ssl_check)
        else:
            r = _api_request_session().get(
                url,
                params=params,
                headers=headers,
                auth=auth,
                verify=disable_ssl_check)
        result = r.json()
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if result and "message" in result:
            raise exception.APIRequestError(result['message'])
        elif result and "errors" in result:
            raise exception.APIRequestError(result['errors'][0]['title'])
        else:
            raise exception.APIRequestError(e)
    except ValueError:
        raise exception.APIRequestError("Invalid response: %s" %
                                        r.text.encode("utf-8"))
    finally:
        if r:
            r.close()
    return result


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
                        return result
            result = _get_api_result(url, params, data)
            if cache_valid:
                with ContentCache() as cc:
                    cc.set(cache_key, result, cache_valid)
            return result
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if not internet_on():
                raise exception.InternetIsOffline()
            from platformio.maintenance import in_silence
            total += 1
            if not in_silence():
                click.secho(
                    "[API] ConnectionError: {0} (incremented retry: max={1}, "
                    "total={2})".format(e, max_retries, total),
                    fg="yellow")
            sleep(2 * total)

    raise exception.APIRequestError(
        "Could not connect to PlatformIO API Service. "
        "Please try later.")


def internet_on(timeout=3):
    host = "8.8.8.8"
    port = 53
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:  # pylint: disable=bare-except
        return False


def get_pythonexe_path():
    return os.environ.get("PYTHONEXEPATH", normpath(sys.executable))


def where_is_program(program, envpath=None):
    env = os.environ
    if envpath:
        env['PATH'] = envpath

    # try OS's built-in commands
    try:
        result = exec_command(
            ["where" if "windows" in get_systype() else "which", program],
            env=env)
        if result['returncode'] == 0 and isfile(result['out'].strip()):
            return result['out'].strip()
    except OSError:
        pass

    # look up in $PATH
    for bin_dir in env.get("PATH", "").split(os.pathsep):
        if isfile(join(bin_dir, program)):
            return join(bin_dir, program)
        elif isfile(join(bin_dir, "%s.exe" % program)):
            return join(bin_dir, "%s.exe" % program)

    return program


def pepver_to_semver(pepver):
    return re.sub(r"(\.\d+)\.?(dev|a|b|rc|post)", r"\1-\2.", pepver, 1)


def rmtree_(path):

    def _onerror(_, name, __):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    return rmtree(path, onerror=_onerror)


#
# Glob.Escape from Python 3.4
# https://github.com/python/cpython/blob/master/Lib/glob.py#L161
#

try:
    from glob import escape as glob_escape  # pylint: disable=unused-import
except ImportError:
    magic_check = re.compile('([*?[])')
    magic_check_bytes = re.compile(b'([*?[])')

    def glob_escape(pathname):
        """Escape all special characters.
        """
        # Escaping is done by wrapping any of "*?[" between square brackets.
        # Metacharacters do not work in the drive part and shouldn't be
        # escaped.
        drive, pathname = os.path.splitdrive(pathname)
        if isinstance(pathname, bytes):
            pathname = magic_check_bytes.sub(br'[\1]', pathname)
        else:
            pathname = magic_check.sub(r'[\1]', pathname)
        return drive + pathname
