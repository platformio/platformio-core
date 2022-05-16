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

import pytest

from platformio.exception import UserSideException
from platformio.package.commands.show import package_show_cmd


def test_spec_name(clirunner, validate_cliresult):
    # library
    result = clirunner.invoke(
        package_show_cmd,
        ["ArduinoJSON"],
    )
    validate_cliresult(result)
    assert "bblanchon/ArduinoJson" in result.output
    assert "Library" in result.output

    # platform
    result = clirunner.invoke(
        package_show_cmd,
        ["espressif32"],
    )
    validate_cliresult(result)
    assert "platformio/espressif32" in result.output
    assert "Platform" in result.output

    # tool
    result = clirunner.invoke(
        package_show_cmd,
        ["tool-jlink"],
    )
    validate_cliresult(result)
    assert "platformio/tool-jlink" in result.output
    assert "tool" in result.output


def test_spec_owner(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_show_cmd,
        ["bblanchon/ArduinoJSON"],
    )
    validate_cliresult(result)
    assert "bblanchon/ArduinoJson" in result.output
    assert "Library" in result.output

    # test broken owner
    result = clirunner.invoke(
        package_show_cmd,
        ["unknown/espressif32"],
    )
    with pytest.raises(UserSideException, match="Could not find"):
        raise result.exception


def test_complete_spec(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_show_cmd,
        ["bblanchon/ArduinoJSON", "-t", "library"],
    )
    validate_cliresult(result)
    assert "bblanchon/ArduinoJson" in result.output
    assert "Library" in result.output

    # tool
    result = clirunner.invoke(
        package_show_cmd,
        ["platformio/tool-jlink", "-t", "tool"],
    )
    validate_cliresult(result)
    assert "platformio/tool-jlink" in result.output
    assert "tool" in result.output


def test_name_conflict(clirunner):
    result = clirunner.invoke(
        package_show_cmd,
        ["OneWire", "-t", "library"],
    )
    assert "More than one package" in result.output
    assert isinstance(result.exception, UserSideException)


def test_spec_version(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_show_cmd,
        ["bblanchon/ArduinoJSON@5.13.4"],
    )
    validate_cliresult(result)
    assert "bblanchon/ArduinoJson" in result.output
    assert "Library • 5.13.4" in result.output
