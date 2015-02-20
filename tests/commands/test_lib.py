# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir
from os.path import isdir, isfile, join

import re

from click.testing import CliRunner

from platformio.commands.lib import cli
from platformio import util

runner = CliRunner()


def validate_output(result):
    assert result.exit_code == 0
    assert not result.exception
    assert "error" not in result.output.lower()


def validate_libfolder():
    libs_path = util.get_lib_dir()
    installed_libs = listdir(libs_path)
    for lib in installed_libs:
        assert isdir(join(libs_path, lib))
        assert isfile(join(libs_path, lib, ".library.json")) and isfile(
            join(libs_path, lib, "library.json"))


def test_lib_search():
    result = runner.invoke(cli, ["search", "DHT22"])
    validate_output(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) > 2

    result = runner.invoke(cli, ["search", "DHT22", "--platform=timsp430"])
    validate_output(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) == 1


def test_lib_install():
    result = runner.invoke(cli, ["install", "58", "115"])
    validate_output(result)
    validate_libfolder()


def test_lib_list():
    result = runner.invoke(cli, ["list"])
    validate_output(result)
    assert "58" in result.output and "115" in result.output


def test_lib_show():
    result = runner.invoke(cli, ["show", "115"])
    validate_output(result)
    assert "arduino" in result.output and "atmelavr" in result.output

    result = runner.invoke(cli, ["show", "58"])
    validate_output(result)
    assert "energia" in result.output and "timsp430" in result.output


def test_lib_update():
    result = runner.invoke(cli, ["update"])
    validate_output(result)
    assert "58" in result.output and "115" in result.output


def test_lib_uninstall():
    result = runner.invoke(cli, ["uninstall", "58", "115"])
    validate_output(result)
