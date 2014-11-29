# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import name as os_name
from os import getcwd, getenv, makedirs, utime
from os.path import dirname, expanduser, isdir, isfile, join, realpath
from platform import system, uname
from subprocess import PIPE, Popen
from time import sleep

import requests
from serial import Serial

from platformio import __apiurl__, __version__
from platformio.exception import (APIRequestError, GetSerialPortsError,
                                  NotPlatformProject)

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def get_systype():
    if system() == "Windows":
        return "windows"
    data = uname()
    return ("%s_%s" % (data[0], data[4])).lower()


def get_home_dir():
    home_dir = None

    try:
        config = get_project_config()
        if (config.has_section("platformio") and
                config.has_option("platformio", "home_dir")):
            home_dir = config.get("platformio", "home_dir")
    except NotPlatformProject:
        pass

    if not home_dir:
        home_dir = expanduser("~/.platformio")

    if not isdir(home_dir):
        makedirs(home_dir)

    assert isdir(home_dir)
    return home_dir


def get_lib_dir():
    try:
        config = get_project_config()
        if (config.has_section("platformio") and
                config.has_option("platformio", "lib_dir")):
            lib_dir = config.get("platformio", "lib_dir")
            if lib_dir.startswith("~"):
                return expanduser(lib_dir)
            else:
                return lib_dir
    except NotPlatformProject:
        pass
    return join(get_home_dir(), "lib")


def get_source_dir():
    return dirname(realpath(__file__))


def get_project_dir():
    return getcwd()


def get_pioenvs_dir():
    return getenv("PIOENVS_DIR", join(get_project_dir(), ".pioenvs"))


def get_project_config():
    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        raise NotPlatformProject()
    cp = ConfigParser()
    cp.read(path)
    return cp


def change_filemtime(path, time):
    utime(path, (time, time))


def exec_command(args):
    use_shell = system() == "Windows"
    p = Popen(args, stdout=PIPE, stderr=PIPE, shell=use_shell)
    out, err = p.communicate()
    return dict(out=out.strip(), err=err.strip())


def reset_serialport(port):
    s = Serial(port)
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def get_serialports():
    if os_name == "nt":
        from serial.tools.list_ports_windows import comports
    elif os_name == "posix":
        from serial.tools.list_ports_posix import comports
    else:
        raise GetSerialPortsError(os_name)
    return[{"port": p, "description": d, "hwid": h} for p, d, h in comports()]


def get_api_result(path, params=None, data=None):
    result = None
    r = None
    try:
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
            raise APIRequestError(result['errors'][0]['title'])
        else:
            raise APIRequestError(e)
    except requests.exceptions.ConnectionError:
        raise APIRequestError(
            "Could not connect to PlatformIO Registry Service")
    except ValueError:
        raise APIRequestError("Invalid response: %s" % r.text)
    finally:
        if r:
            r.close()
    return result
