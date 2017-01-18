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

import json
import os
from os.path import join

from platformio import exception, util
from platformio.commands import platform as cli_platform


def test_list_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list, ["--json-output"])
    validate_cliresult(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert len(list_result)
    platforms = [item['name'] for item in list_result]
    assert "titiva" in platforms


def test_list_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list)
    validate_cliresult(result)
    assert "teensy" in result.output


def test_search_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_search,
                              ["arduino", "--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['name'] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_search, ["arduino"])
    validate_cliresult(result)
    assert "teensy" in result.output


def test_install_uknown_from_registry(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_install,
                              ["uknown-platform"])
    assert result.exit_code == -1
    assert isinstance(result.exception, exception.UnknownPackage)


def test_install_from_vcs(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_install, [
        "https://github.com/platformio/"
        "platform-espressif8266.git#feature/stage"
    ])
    validate_cliresult(result)
    assert "espressif8266_stage" in result.output


def test_install_uknown_version(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_install,
                              ["atmelavr@99.99.99"])
    assert result.exit_code == -1
    assert isinstance(result.exception, exception.UndefinedPackageVersion)


def test_complex(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        os.environ["PLATFORMIO_HOME_DIR"] = os.getcwd()
        try:
            result = clirunner.invoke(
                cli_platform.platform_install,
                ["teensy", "--with-package", "framework-arduinoteensy"])
            validate_cliresult(result)
            assert all([
                s in result.output
                for s in ("teensy", "Downloading", "Unpacking")
            ])

            # show platform information
            result = clirunner.invoke(cli_platform.platform_show, ["teensy"])
            validate_cliresult(result)
            assert "teensy" in result.output

            # list platforms
            result = clirunner.invoke(cli_platform.platform_list,
                                      ["--json-output"])
            validate_cliresult(result)
            list_result = json.loads(result.output)
            assert isinstance(list_result, list)
            assert len(list_result) == 1
            assert list_result[0]["name"] == "teensy"
            assert list_result[0]["packages"] == ["framework-arduinoteensy"]

            # try to install again
            result = clirunner.invoke(cli_platform.platform_install,
                                      ["teensy"])
            validate_cliresult(result)
            assert "is already installed" in result.output

            # try to update
            for _ in range(2):
                result = clirunner.invoke(cli_platform.platform_update)
                validate_cliresult(result)
                assert "teensy" in result.output
                assert "Up-to-date" in result.output
                assert "Out-of-date" not in result.output

            # try to uninstall
            result = clirunner.invoke(cli_platform.platform_uninstall,
                                      ["teensy"])
            validate_cliresult(result)
            for folder in ("platforms", "packages"):
                assert len(os.listdir(join(util.get_home_dir(), folder))) == 0
        finally:
            del os.environ["PLATFORMIO_HOME_DIR"]
