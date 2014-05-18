# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from sys import exit
from os import getcwd
from os.path import dirname, expanduser, join, realpath, isfile
from subprocess import Popen, PIPE

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
    try:
        return getattr(get_project_config, "_cache")
    except AttributeError:
        pass

    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        exit("Not a platformio project. Use `platformio init` command")

    get_project_config._cache = ConfigParser()
    get_project_config._cache.read(path)
    return get_project_config._cache


def exec_command(args):
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    result = dict(out=out.strip(), err=err.strip())

    # fix STDERR "flash written"
    if "flash written" in result['err']:
        result['out'] += "\n" + result['err']
        result['err'] = ""

    return result


def run_builder(variables, targets):
    assert isinstance(variables, list)
    assert isinstance(targets, list)

    if "clean" in targets:
        targets.remove("clean")
        targets.append("-c")

    return exec_command([
        "scons",
        "-Q",
        "-f", join(get_source_dir(), "builder", "main.py")
    ] + variables + targets)
