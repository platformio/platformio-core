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

from platformio import exception
from platformio.commands import platform as cli_platform


def test_search_json_output(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli_platform.platform_search,
                              ["arduino", "--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert search_result
    platforms = [item['name'] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_search, ["arduino"])
    validate_cliresult(result)
    assert "teensy" in result.output


def test_install_unknown_version(clirunner):
    result = clirunner.invoke(cli_platform.platform_install,
                              ["atmelavr@99.99.99"])
    assert result.exit_code == -1
    assert isinstance(result.exception, exception.UndefinedPackageVersion)


def test_install_unknown_from_registry(clirunner):
    result = clirunner.invoke(cli_platform.platform_install,
                              ["unknown-platform"])
    assert result.exit_code == -1
    assert isinstance(result.exception, exception.UnknownPackage)


def test_install_known_version(clirunner, validate_cliresult,
                               isolated_pio_home):
    result = clirunner.invoke(cli_platform.platform_install, [
        "atmelavr@1.2.0", "--skip-default-package", "--with-package",
        "tool-avrdude"
    ])
    validate_cliresult(result)
    assert "atmelavr @ 1.2.0" in result.output
    assert "Installing tool-avrdude @" in result.output
    assert len(isolated_pio_home.join("packages").listdir()) == 1


def test_install_from_vcs(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_install, [
        "https://github.com/platformio/"
        "platform-espressif8266.git#feature/stage", "--skip-default-package"
    ])
    validate_cliresult(result)
    assert "espressif8266" in result.output


def test_list_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list, ["--json-output"])
    validate_cliresult(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert list_result
    platforms = [item['name'] for item in list_result]
    assert set(["atmelavr", "espressif8266"]) == set(platforms)


def test_list_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list)
    validate_cliresult(result)
    assert all(
        [s in result.output for s in ("atmelavr", "espressif8266")])


def test_update_check(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli_platform.platform_update,
                              ["--only-check", "--json-output"])
    validate_cliresult(result)
    output = json.loads(result.output)
    assert len(output) == 1
    assert output[0]['name'] == "atmelavr"
    assert len(isolated_pio_home.join("packages").listdir()) == 1


def test_update_raw(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli_platform.platform_update)
    validate_cliresult(result)
    assert "Uninstalling atmelavr @ 1.2.0:" in result.output
    assert "PlatformManager: Installing atmelavr @" in result.output
    assert len(isolated_pio_home.join("packages").listdir()) == 1


def test_uninstall(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli_platform.platform_uninstall,
                              ["atmelavr", "espressif8266"])
    validate_cliresult(result)
    assert not isolated_pio_home.join("platforms").listdir()
