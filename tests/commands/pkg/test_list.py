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

# pylint: disable=unused-argument

from platformio.package.commands.install import package_install_cmd
from platformio.package.commands.list import package_list_cmd

PROJECT_CONFIG_TPL = """
[env]
platform = platformio/atmelavr@^3.4.0

[env:baremetal]
board = uno

[env:devkit]
framework = arduino
board = attiny88
lib_deps =
    milesburton/DallasTemperature@^3.9.1
    https://github.com/bblanchon/ArduinoJson.git#v6.19.0
"""


def test_project(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir)],
    )
    validate_cliresult(result)

    # test all envs
    result = clirunner.invoke(
        package_list_cmd,
        ["-d", str(project_dir)],
    )
    validate_cliresult(result)
    assert all(token in result.output for token in ("baremetal", "devkit"))
    assert result.output.count("Platform atmelavr @ 3.4.0") == 2
    assert (
        result.output.count(
            "toolchain-atmelavr @ 1.70300.191015 (required: "
            "platformio/toolchain-atmelavr @ ~1.70300.0)"
        )
        == 2
    )
    assert result.output.count("Libraries") == 1
    assert (
        "ArduinoJson @ 6.19.0+sha.9693fd2 (required: "
        "git+https://github.com/bblanchon/ArduinoJson.git#v6.19.0)"
    ) in result.output
    assert "OneWire @ 2" in result.output

    # test "baremetal"
    result = clirunner.invoke(
        package_list_cmd,
        ["-d", str(project_dir), "-e", "baremetal"],
    )
    validate_cliresult(result)
    assert "Platform atmelavr @ 3" in result.output
    assert "Libraries" not in result.output

    # filter by "tool" package
    result = clirunner.invoke(
        package_list_cmd,
        ["-d", str(project_dir), "-t", "toolchain-atmelavr@~1.70300.0"],
    )
    assert "framework-arduino" not in result.output
    assert "Libraries" not in result.output

    # list only libraries
    result = clirunner.invoke(
        package_list_cmd,
        ["-d", str(project_dir), "--only-libraries"],
    )
    assert "Platform atmelavr" not in result.output

    # list only libraries for baremetal
    result = clirunner.invoke(
        package_list_cmd,
        ["-d", str(project_dir), "-e", "baremetal", "--only-libraries"],
    )
    assert "No packages" in result.output


def test_global_packages(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    result = clirunner.invoke(package_list_cmd, ["-g"])
    validate_cliresult(result)
    assert "atmelavr @ 3" in result.output
    assert "framework-arduino-avr-attiny" in result.output

    # only tools
    result = clirunner.invoke(package_list_cmd, ["-g", "--only-tools"])
    validate_cliresult(result)
    assert "toolchain-atmelavr" in result.output
    assert "Platforms" not in result.output

    # find tool package
    result = clirunner.invoke(package_list_cmd, ["-g", "-t", "toolchain-atmelavr"])
    validate_cliresult(result)
    assert "toolchain-atmelavr" in result.output
    assert "framework-arduino-avr-attiny@" not in result.output

    # only libraries - no packages
    result = clirunner.invoke(package_list_cmd, ["-g", "--only-libraries"])
    validate_cliresult(result)
    assert not result.output.strip()

    # check global libs
    result = clirunner.invoke(
        package_install_cmd, ["-g", "-l", "milesburton/DallasTemperature@^3.9.1"]
    )
    validate_cliresult(result)
    result = clirunner.invoke(package_list_cmd, ["-g", "--only-libraries"])
    validate_cliresult(result)
    assert "DallasTemperature" in result.output
    assert "OneWire" in result.output

    # filter by lib
    result = clirunner.invoke(package_list_cmd, ["-g", "-l", "OneWire"])
    validate_cliresult(result)
    assert "DallasTemperature" in result.output
    assert "OneWire" in result.output
