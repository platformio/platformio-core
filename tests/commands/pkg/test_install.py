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

import os

import pytest

from platformio import fs
from platformio.package.commands.install import package_install_cmd
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.project.config import ProjectConfig

PROJECT_CONFIG_TPL = """
[env]
platform = platformio/atmelavr@^3.4.0
lib_deps = milesburton/DallasTemperature@^3.9.1

[env:baremetal]
board = uno

[env:devkit]
framework = arduino
board = attiny88
"""


def pkgs_to_names(pkgs):
    return [pkg.metadata.name for pkg in pkgs]


def test_skip_dependencies(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "--skip-dependencies"],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        installed_lib_pkgs = LibraryPackageManager(
            os.path.join(ProjectConfig().get("platformio", "libdeps_dir"), "devkit")
        ).get_installed()
        assert pkgs_to_names(installed_lib_pkgs) == ["DallasTemperature"]
        assert len(ToolPackageManager().get_installed()) == 0


def test_baremetal_project(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "baremetal"],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        installed_lib_pkgs = LibraryPackageManager(
            os.path.join(ProjectConfig().get("platformio", "libdeps_dir"), "baremetal")
        ).get_installed()
        assert pkgs_to_names(installed_lib_pkgs) == ["DallasTemperature", "OneWire"]
        assert pkgs_to_names(ToolPackageManager().get_installed()) == [
            "toolchain-atmelavr"
        ]


def test_project(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir)],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        config = ProjectConfig()
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        assert pkgs_to_names(lm.get_installed()) == ["DallasTemperature", "OneWire"]
        assert pkgs_to_names(ToolPackageManager().get_installed()) == [
            "framework-arduino-avr-attiny",
            "toolchain-atmelavr",
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.9.1"
        ]


def test_unknown_project_dependencies(
    clirunner, validate_cliresult, isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(
        """
[env:unknown_platform]
platform = unknown_platform

[env:unknown_lib_deps]
lib_deps = SPI, platformio/unknown_library
"""
    )
    with fs.cd(str(project_dir)):
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "unknown_platform"],
        )
        with pytest.raises(
            AssertionError,
            match=("Could not find the package with 'unknown_platform' requirements"),
        ):
            validate_cliresult(result)

        # unknown libraries
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "unknown_lib_deps"],
        )
        with pytest.raises(
            AssertionError,
            match=(
                "Could not find the package with 'platformio/unknown_library' requirements"
            ),
        ):
            validate_cliresult(result)


def test_custom_project_libraries(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    spec = "bblanchon/ArduinoJson@^6.19.2"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-l", spec],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        # try again
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-l", spec],
        )
        validate_cliresult(result)
        assert "already installed" in result.output
        # try again in the silent mode
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-l", spec, "--silent"],
        )
        validate_cliresult(result)
        assert not result.output.strip()

        # check folders
        config = ProjectConfig()
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        assert pkgs_to_names(lm.get_installed()) == ["ArduinoJson"]
        # do not expect any platforms/tools
        assert not os.path.exists(config.get("platformio", "platforms_dir"))
        assert not os.path.exists(config.get("platformio", "packages_dir"))
        # check saved deps
        assert config.get("env:devkit", "lib_deps") == [
            "bblanchon/ArduinoJson@^6.19.2",
        ]

        # install library without saving to config
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-l", "nanopb/Nanopb@^0.4.6", "--no-save"],
        )
        validate_cliresult(result)
        config = ProjectConfig()
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        assert pkgs_to_names(lm.get_installed()) == ["ArduinoJson", "Nanopb"]
        assert config.get("env:devkit", "lib_deps") == [
            "bblanchon/ArduinoJson@^6.19.2",
        ]

        # unknown libraries
        result = clirunner.invoke(
            package_install_cmd, ["-l", "platformio/unknown_library"]
        )
        with pytest.raises(
            AssertionError,
            match=(
                "Could not find the package with "
                "'platformio/unknown_library' requirements"
            ),
        ):
            validate_cliresult(result)


def test_custom_project_tools(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    spec = "platformio/tool-openocd"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-t", spec],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        # try again
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-t", spec],
        )
        validate_cliresult(result)
        assert "already installed" in result.output
        # try again in the silent mode
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-t", spec, "--silent"],
        )
        validate_cliresult(result)
        assert not result.output.strip()

        config = ProjectConfig()
        assert pkgs_to_names(ToolPackageManager().get_installed()) == ["tool-openocd"]
        assert not LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        ).get_installed()
        # do not expect any platforms
        assert not os.path.exists(config.get("platformio", "platforms_dir"))

        # unknown tool
        result = clirunner.invoke(
            package_install_cmd, ["-t", "platformio/unknown_tool"]
        )
        with pytest.raises(
            AssertionError,
            match=(
                "Could not find the package with "
                "'platformio/unknown_tool' requirements"
            ),
        ):
            validate_cliresult(result)


def test_custom_project_platforms(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    spec = "atmelavr"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-p", spec, "--skip-dependencies"],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        # try again
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-p", spec, "--skip-dependencies"],
        )
        validate_cliresult(result)
        assert "already installed" in result.output
        # try again in the silent mode
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-p", spec, "--silent", "--skip-dependencies"],
        )
        validate_cliresult(result)
        assert not result.output.strip()

        config = ProjectConfig()
        assert pkgs_to_names(PlatformPackageManager().get_installed()) == ["atmelavr"]
        assert not LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        ).get_installed()
        # do not expect any packages
        assert not os.path.exists(config.get("platformio", "packages_dir"))

        # unknown platform
        result = clirunner.invoke(package_install_cmd, ["-p", "unknown_platform"])
        with pytest.raises(
            AssertionError,
            match="Could not find the package with 'unknown_platform' requirements",
        ):
            validate_cliresult(result)

        # incompatible board
        result = clirunner.invoke(package_install_cmd, ["-e", "devkit", "-p", "sifive"])
        with pytest.raises(
            AssertionError,
            match="Unknown board ID",
        ):
            validate_cliresult(result)


def test_global_packages(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    # libraries
    result = clirunner.invoke(
        package_install_cmd,
        [
            "--global",
            "-l",
            "milesburton/DallasTemperature@^3.9.1",
            "--skip-dependencies",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_names(LibraryPackageManager().get_installed()) == [
        "DallasTemperature"
    ]
    # with dependencies
    result = clirunner.invoke(
        package_install_cmd,
        [
            "--global",
            "-l",
            "milesburton/DallasTemperature@^3.9.1",
            "-l",
            "bblanchon/ArduinoJson@^6.19.2",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_names(LibraryPackageManager().get_installed()) == [
        "ArduinoJson",
        "DallasTemperature",
        "OneWire",
    ]
    # custom storage
    storage_dir = tmp_path / "custom_lib_storage"
    storage_dir.mkdir()
    result = clirunner.invoke(
        package_install_cmd,
        [
            "--global",
            "--storage-dir",
            str(storage_dir),
            "-l",
            "bblanchon/ArduinoJson@^6.19.2",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_names(LibraryPackageManager(storage_dir).get_installed()) == [
        "ArduinoJson"
    ]

    # tools
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-t", "platformio/framework-arduino-avr-attiny@^1.5.2"],
    )
    validate_cliresult(result)
    assert pkgs_to_names(ToolPackageManager().get_installed()) == [
        "framework-arduino-avr-attiny"
    ]

    # platforms
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-p", "platformio/atmelavr@^3.4.0", "--skip-dependencies"],
    )
    validate_cliresult(result)
    assert pkgs_to_names(PlatformPackageManager().get_installed()) == ["atmelavr"]
