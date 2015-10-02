# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import collections
import functools
import json
import os
import re
import subprocess
from os.path import (abspath, basename, dirname, expanduser, isdir, isfile,
                     join, realpath)
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
        return functools.partial(self.__call__, obj)


def singleton(cls):
    """ From PEP-318 http://www.python.org/dev/peps/pep-0318/#examples """
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return get_instance


def get_systype():
    data = uname()
    type_ = data[0].lower()
    arch = data[4].lower() if data[4] else ""
    return "%s_%s" % (type_, arch) if arch else type_


def pioversion_to_intstr():
    vermatch = re.match(r"^([\d\.]+)", __version__)
    assert vermatch
    return [int(i) for i in vermatch.group(1).split(".")[:3]]


def _get_projconf_option_dir(name, default=None):
    _env_name = "PLATFORMIO_%s" % name.upper()
    if _env_name in os.environ:
        return os.getenv(_env_name)

    try:
        config = get_project_config()
        if (config.has_section("platformio") and
                config.has_option("platformio", name)):
            option_dir = config.get("platformio", name)
            if option_dir.startswith("~"):
                option_dir = expanduser(option_dir)
            return abspath(option_dir)
    except exception.NotPlatformProject:
        pass
    return default


def get_home_dir():
    home_dir = _get_projconf_option_dir(
        "home_dir",
        join(expanduser("~"), ".platformio")
    )

    if not isdir(home_dir):
        os.makedirs(home_dir)

    assert isdir(home_dir)
    return home_dir


def get_lib_dir():
    return _get_projconf_option_dir(
        "lib_dir",
        join(get_home_dir(), "lib")
    )


def get_source_dir():
    return dirname(realpath(__file__))


def get_project_dir():
    return os.getcwd()


def get_projectsrc_dir():
    return _get_projconf_option_dir(
        "src_dir",
        join(get_project_dir(), "src")
    )


def get_projectlib_dir():
    return join(get_project_dir(), "lib")


def get_pioenvs_dir():
    return _get_projconf_option_dir(
        "envs_dir",
        join(get_project_dir(), ".pioenvs")
    )


def get_project_config():
    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        raise exception.NotPlatformProject(get_project_dir())
    cp = ConfigParser()
    cp.read(path)
    return cp


def change_filemtime(path, time):
    os.utime(path, (time, time))


def is_ci():
    return os.getenv("CI", "").lower() == "true"


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
    return [{"port": p, "description": d, "hwid": h}
            for p, d, h in comports() if p]


def get_logicaldisks():
    disks = []
    if system() == "Windows":
        result = exec_command(
            ["wmic", "logicaldisk", "get", "name,VolumeName"]).get("out")
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
            disks.append({"disk": match.group(1),
                          "name": basename(match.group(1))})
    return disks


def get_request_defheaders():
    return {"User-Agent": "PlatformIO/%s CI/%d %s" % (
        __version__, int(is_ci()), requests.utils.default_user_agent()
    )}


def get_api_result(path, params=None, data=None):
    result = None
    r = None

    try:
        if data:
            r = requests.post(__apiurl__ + path, params=params, data=data,
                              headers=get_request_defheaders())
        else:
            r = requests.get(__apiurl__ + path, params=params,
                             headers=get_request_defheaders())
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


@memoized
def _lookup_boards():
    boards = {}
    bdirs = [join(get_source_dir(), "boards")]
    if isdir(join(get_home_dir(), "boards")):
        bdirs.append(join(get_home_dir(), "boards"))

    for bdir in bdirs:
        for json_file in sorted(os.listdir(bdir)):
            if not json_file.endswith(".json"):
                continue
            with open(join(bdir, json_file)) as f:
                boards.update(json.load(f))
    return boards


def get_boards(type_=None):
    boards = _lookup_boards()

    if type_ is None:
        return boards
    else:
        if type_ not in boards:
            raise exception.UnknownBoard(type_)
        return boards[type_]


@memoized
def _lookup_frameworks():
    frameworks = {}
    frameworks_path = join(
        get_source_dir(), "builder", "scripts", "frameworks")

    frameworks_list = [f[:-3] for f in os.listdir(frameworks_path)
                       if not f.startswith("__") and f.endswith(".py")]
    for _type in frameworks_list:
        script_path = join(frameworks_path, "%s.py" % _type)
        with open(script_path) as f:
            fcontent = f.read()
            assert '"""' in fcontent
            _doc_start = fcontent.index('"""') + 3
            fdoc = fcontent[
                _doc_start:fcontent.index('"""', _doc_start)].strip()
            doclines = [l.strip() for l in fdoc.splitlines() if l.strip()]
            frameworks[_type] = {
                "name": doclines[0],
                "description": " ".join(doclines[1:-1]),
                "url": doclines[-1],
                "script": script_path
            }
    return frameworks


def get_frameworks(type_=None):
    frameworks = _lookup_frameworks()

    if type_ is None:
        return frameworks
    else:
        if type_ not in frameworks:
            raise exception.UnknownFramework(type_)
        return frameworks[type_]

    return frameworks


def where_is_program(program, envpath=None):
    env = os.environ
    if envpath:
        env['PATH'] = envpath

    # try OS's built-in commands
    try:
        result = exec_command(
            ["where" if "windows" in get_systype() else "which", program],
            env=env
        )
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
