# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
import os
import subprocess
from os.path import abspath, dirname, expanduser, isdir, isfile, join, realpath
from platform import system, uname
from threading import Thread

import requests

from platformio import __apiurl__, __version__, exception

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


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


def get_systype():
    data = uname()
    return ("%s_%s" % (data[0], data[4])).lower()


def _get_projconf_option_dir(option_name):
    try:
        config = get_project_config()
        if (config.has_section("platformio") and
                config.has_option("platformio", option_name)):
            option_dir = config.get("platformio", option_name)
            if option_dir.startswith("~"):
                option_dir = expanduser(option_dir)
            return abspath(option_dir)
    except exception.NotPlatformProject:
        pass
    return None


def get_home_dir():
    home_dir = _get_projconf_option_dir("home_dir")

    if not home_dir:
        home_dir = join(expanduser("~"), ".platformio")

    if not isdir(home_dir):
        os.makedirs(home_dir)

    assert isdir(home_dir)
    return home_dir


def get_lib_dir():
    lib_dir = _get_projconf_option_dir("lib_dir")

    if not lib_dir:
        lib_dir = join(get_home_dir(), "lib")

    return lib_dir


def get_source_dir():
    return dirname(realpath(__file__))


def get_project_dir():
    return os.getcwd()


def get_projectsrc_dir():
    src_dir = _get_projconf_option_dir("src_dir")

    if not src_dir:
        src_dir = join(get_project_dir(), "src")

    return src_dir


def get_pioenvs_dir():
    return os.getenv("PIOENVS_DIR", join(get_project_dir(), ".pioenvs"))


def get_project_config():
    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        raise exception.NotPlatformProject(get_project_dir())
    cp = ConfigParser()
    cp.read(path)
    return cp


def change_filemtime(path, time):
    os.utime(path, (time, time))


def exec_command(*args, **kwargs):
    result = {
        "out": None,
        "err": None,
        "returncode": None
    }

    default = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=system() == "Windows"
    )
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


def get_serialports():
    if os.name == "nt":
        from serial.tools.list_ports_windows import comports
    elif os.name == "posix":
        from serial.tools.list_ports_posix import comports
    else:
        raise exception.GetSerialPortsError(os.name)
    return[{"port": p, "description": d, "hwid": h} for p, d, h in comports()]


def get_api_result(path, params=None, data=None):
    result = None
    r = None

    try:
        requests.packages.urllib3.disable_warnings()
        headers = {"User-Agent": "PlatformIO/%s %s" % (
            __version__, requests.utils.default_user_agent())}

        if data:
            r = requests.post(__apiurl__ + path, params=params, data=data,
                              headers=headers)
        else:
            r = requests.get(__apiurl__ + path, params=params, headers=headers)
        result = r.json()
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if result and "errors" in result:
            raise exception.APIRequestError(result['errors'][0]['title'])
        else:
            raise exception.APIRequestError(e)
    except requests.exceptions.ConnectionError:
        raise exception.APIRequestError(
            "Could not connect to PlatformIO Registry Service")
    except ValueError:
        raise exception.APIRequestError(
            "Invalid response: %s" % r.text.encode("utf-8"))
    finally:
        if r:
            r.close()
    return result


def get_boards(type_=None):
    boards = {}
    try:
        boards = get_boards._cache  # pylint: disable=W0212
    except AttributeError:
        bdirs = [join(get_source_dir(), "boards")]
        if isdir(join(get_home_dir(), "boards")):
            bdirs.append(join(get_home_dir(), "boards"))

        for bdir in bdirs:
            for json_file in os.listdir(bdir):
                if not json_file.endswith(".json"):
                    continue
                with open(join(bdir, json_file)) as f:
                    boards.update(json.load(f))
        get_boards._cache = boards  # pylint: disable=W0212

    if type_ is None:
        return boards
    else:
        if type_ not in boards:
            raise exception.UnknownBoard(type_)
        return boards[type_]
