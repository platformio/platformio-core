# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

from os import listdir
from os.path import isdir, isfile, join

import re

from platformio.commands.lib import cli
from platformio import util


def validate_libfolder():
    libs_path = util.get_lib_dir()
    installed_libs = listdir(libs_path)
    for lib in installed_libs:
        assert isdir(join(libs_path, lib))
        assert isfile(join(libs_path, lib, ".library.json")) and isfile(
            join(libs_path, lib, "library.json"))


def test_lib_search(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["search", "DHT22"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) > 2

    result = clirunner.invoke(cli, ["search", "DHT22", "--platform=timsp430"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) == 1


def test_lib_install(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["install", "58", "115"])
    validate_cliresult(result)
    validate_libfolder()


def test_lib_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["list"])
    validate_cliresult(result)
    assert "58" in result.output and "115" in result.output


def test_lib_show(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["show", "115"])
    validate_cliresult(result)
    assert "arduino" in result.output and "atmelavr" in result.output

    result = clirunner.invoke(cli, ["show", "58"])
    validate_cliresult(result)
    assert "energia" in result.output and "timsp430" in result.output


def test_lib_update(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["update"])
    validate_cliresult(result)
    assert "58" in result.output and "115" in result.output


def test_lib_uninstall(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["uninstall", "58", "115"])
    validate_cliresult(result)
