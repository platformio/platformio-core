# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, utime
from os.path import dirname, expanduser, isfile, join, realpath
from platform import architecture, system
from subprocess import PIPE, Popen

from platformio.exception import NotPlatformProject

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def get_home_dir():
    return expanduser("~/.platformio")


def get_source_dir():
    return dirname(realpath(__file__))


def get_project_dir():
    return getcwd()


def get_project_config():
    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        raise NotPlatformProject()
    cp = ConfigParser()
    cp.read(path)
    return cp


def get_system():
    return (system() + architecture()[0][:-3]).lower()


def change_filemtime(path, time):
    utime(path, (time, time))


def exec_command(args):
    use_shell = get_system() == "windows32"
    p = Popen(args, stdout=PIPE, stderr=PIPE, shell=use_shell)
    out, err = p.communicate()
    return dict(out=out.strip(), err=err.strip())
