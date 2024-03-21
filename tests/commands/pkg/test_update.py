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

from platformio import fs
from platformio.dependencies import get_core_dependencies
from platformio.package.commands.install import package_install_cmd
from platformio.package.commands.update import package_update_cmd
from platformio.package.exception import UnknownPackageError
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.project.config import ProjectConfig

DALLASTEMPERATURE_LATEST_VERSION = "3.11.0"

PROJECT_OUTDATED_CONFIG_TPL = """
[env:devkit]
platform = platformio/atmelavr@^2
framework = arduino
board = attiny88
lib_deps = milesburton/DallasTemperature@^3.8.0
"""

PROJECT_UPDATED_CONFIG_TPL = """
[env:devkit]
platform = platformio/atmelavr@<4
framework = arduino
board = attiny88
lib_deps = milesburton/DallasTemperature@^3.8.0
"""


def pkgs_to_specs(pkgs):
    return [
        PackageSpec(name=pkg.metadata.name, requirements=pkg.metadata.version)
        for pkg in pkgs
    ]


def test_global_packages(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    # libraries
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-l", "bblanchon/ArduinoJson@^5"],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(LibraryPackageManager().get_installed()) == [
        PackageSpec("ArduinoJson@5.13.4")
    ]
    # update to the latest version
    result = clirunner.invoke(
        package_update_cmd,
        ["--global", "-l", "bblanchon/ArduinoJson"],
    )
    validate_cliresult(result)
    pkgs = LibraryPackageManager().get_installed()
    assert len(pkgs) == 1
    assert pkgs[0].metadata.version.major > 5
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
            "bblanchon/ArduinoJson@^5",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(LibraryPackageManager(storage_dir).get_installed()) == [
        PackageSpec("ArduinoJson@5.13.4")
    ]
    # update to the latest version
    result = clirunner.invoke(
        package_update_cmd,
        ["--global", "--storage-dir", str(storage_dir), "-l", "bblanchon/ArduinoJson"],
    )
    validate_cliresult(result)
    pkgs = LibraryPackageManager(storage_dir).get_installed()
    assert len(pkgs) == 1
    assert pkgs[0].metadata.version.major > 5

    # tools
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-t", "platformio/framework-arduino-avr-attiny@~1.4"],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
        PackageSpec("framework-arduino-avr-attiny@1.4.1")
    ]
    # update to the latest version
    result = clirunner.invoke(
        package_update_cmd,
        ["--global", "-t", "platformio/framework-arduino-avr-attiny@^1"],
    )
    validate_cliresult(result)
    pkgs = ToolPackageManager().get_installed()
    assert len(pkgs) == 1
    assert pkgs[0].metadata.version.major == 1
    assert pkgs[0].metadata.version.minor > 4

    # platforms
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-p", "platformio/atmelavr@^2", "--skip-dependencies"],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
        PackageSpec("atmelavr@2.2.0")
    ]
    # update to the latest version
    result = clirunner.invoke(
        package_update_cmd,
        ["--global", "-p", "platformio/atmelavr", "--skip-dependencies"],
    )
    validate_cliresult(result)
    pkgs = PlatformPackageManager().get_installed()
    assert len(pkgs) == 1
    assert pkgs[0].metadata.version.major > 2

    # update unknown package
    result = clirunner.invoke(
        package_update_cmd,
        ["--global", "-l", "platformio/unknown_package_for_update"],
    )
    assert isinstance(result.exception, UnknownPackageError)


def test_project(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_OUTDATED_CONFIG_TPL)
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
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(f"DallasTemperature@{DALLASTEMPERATURE_LATEST_VERSION}"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
            PackageSpec("atmelavr@2.2.0")
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("framework-arduino-avr-attiny@1.3.2"),
            PackageSpec("tool-scons@%s" % get_core_dependencies()["tool-scons"][1:]),
            PackageSpec("toolchain-atmelavr@1.50400.190710"),
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.8.0"
        ]

        # update packages
        (project_dir / "platformio.ini").write_text(PROJECT_UPDATED_CONFIG_TPL)
        result = clirunner.invoke(package_update_cmd)
        validate_cliresult(result)
        config = ProjectConfig()
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        pkgs = PlatformPackageManager().get_installed()
        assert len(pkgs) == 1
        assert pkgs[0].metadata.name == "atmelavr"
        assert pkgs[0].metadata.version.major == 3
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("framework-arduino-avr-attiny@1.3.2"),
            PackageSpec("tool-scons@%s" % get_core_dependencies()["tool-scons"][1:]),
            PackageSpec("toolchain-atmelavr@1.70300.191015"),
            PackageSpec("toolchain-atmelavr@1.50400.190710"),
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.8.0"
        ]

        # update again
        result = clirunner.invoke(package_update_cmd)
        validate_cliresult(result)
        assert "Already up-to-date." in result.output

        # update again in the silent ,pde
        result = clirunner.invoke(package_update_cmd, ["--silent"])
        validate_cliresult(result)
        assert not result.output


def test_custom_project_libraries(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_OUTDATED_CONFIG_TPL)
    spec = "milesburton/DallasTemperature@^3.8.0"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-l", spec],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        config = ProjectConfig()
        assert config.get("env:devkit", "lib_deps") == [spec]
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(f"DallasTemperature@{DALLASTEMPERATURE_LATEST_VERSION}"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        # update package
        result = clirunner.invoke(
            package_update_cmd,
            ["-e", "devkit", "-l", "milesburton/DallasTemperature@^3.8.0"],
        )
        assert ProjectConfig().get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.8.0"
        ]
        # try again
        result = clirunner.invoke(
            package_update_cmd,
            ["-e", "devkit", "-l", "milesburton/DallasTemperature@^3.8.0"],
        )
        validate_cliresult(result)
        assert "Already up-to-date." in result.output

        # install library without saving to config
        result = clirunner.invoke(
            package_update_cmd,
            ["-e", "devkit", "-l", "milesburton/DallasTemperature@^3", "--no-save"],
        )
        validate_cliresult(result)
        assert "Already up-to-date." in result.output
        config = ProjectConfig()
        lm = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        )
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.8.0"
        ]

        # unknown libraries
        result = clirunner.invoke(
            package_update_cmd, ["-l", "platformio/unknown_library"]
        )
        assert isinstance(result.exception, UnknownPackageError)


def test_custom_project_tools(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_OUTDATED_CONFIG_TPL)
    spec = "toolchain-atmelavr@~1.50400.0"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-t", spec],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        assert ProjectConfig().get("env:devkit", "platform_packages") == [
            "platformio/toolchain-atmelavr@~1.50400.0"
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("toolchain-atmelavr@1.50400.190710")
        ]
        result = clirunner.invoke(
            package_update_cmd,
            ["-e", "devkit", "-t", "toolchain-atmelavr@^1"],
        )
        validate_cliresult(result)
        assert ProjectConfig().get("env:devkit", "platform_packages") == [
            "platformio/toolchain-atmelavr@^1"
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("toolchain-atmelavr@1.70300.191015")
        ]

        # install without saving to config
        result = clirunner.invoke(
            package_update_cmd,
            ["-e", "devkit", "-t", "toolchain-atmelavr@~1.70300.191015", "--no-save"],
        )
        validate_cliresult(result)
        assert "Already up-to-date." in result.output
        assert ProjectConfig().get("env:devkit", "platform_packages") == [
            "platformio/toolchain-atmelavr@^1"
        ]

        # unknown tool
        result = clirunner.invoke(package_update_cmd, ["-t", "platformio/unknown_tool"])
        assert isinstance(result.exception, UnknownPackageError)


def test_custom_project_platforms(
    clirunner, validate_cliresult, func_isolated_pio_core, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_OUTDATED_CONFIG_TPL)
    spec = "atmelavr@^2"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "devkit", "-p", spec, "--skip-dependencies"],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
            PackageSpec("atmelavr@2.2.0")
        ]
        assert ProjectConfig().get("env:devkit", "platform") == "platformio/atmelavr@^2"

        # update
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-p", "platformio/atmelavr@^3", "--skip-dependencies"],
        )
        validate_cliresult(result)
        assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
            PackageSpec("atmelavr@3.4.0"),
            PackageSpec("atmelavr@2.2.0"),
        ]
        assert ProjectConfig().get("env:devkit", "platform") == "platformio/atmelavr@^2"

        # unknown platform
        result = clirunner.invoke(package_install_cmd, ["-p", "unknown_platform"])
        assert isinstance(result.exception, UnknownPackageError)
