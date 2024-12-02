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
from platformio.dependencies import get_core_dependencies
from platformio.package.commands.install import package_install_cmd
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.project.config import ProjectConfig

PROJECT_CONFIG_TPL = """
[env]
platform = platformio/atmelavr@^3.4.0
lib_deps =
    milesburton/DallasTemperature@^3.9.1
    https://github.com/esphome/ESPAsyncWebServer/archive/refs/tags/v2.1.0.zip

[env:baremetal]
board = uno

[env:devkit]
framework = arduino
board = attiny88
"""


def pkgs_to_specs(pkgs):
    return [
        PackageSpec(name=pkg.metadata.name, requirements=pkg.metadata.version)
        for pkg in pkgs
    ]


def test_global_packages(
    clirunner,
    validate_cliresult,
    func_isolated_pio_core,
    get_pkg_latest_version,
    tmp_path,
):
    # libraries
    result = clirunner.invoke(
        package_install_cmd,
        [
            "--global",
            "-l",
            "https://github.com/milesburton/Arduino-Temperature-Control-Library.git#3.9.0",
            "--skip-dependencies",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(LibraryPackageManager().get_installed()) == [
        PackageSpec("DallasTemperature@3.9.0+sha.964939d")
    ]
    # with dependencies
    result = clirunner.invoke(
        package_install_cmd,
        [
            "--global",
            "-l",
            "https://github.com/milesburton/Arduino-Temperature-Control-Library.git#3.9.0",
            "-l",
            "bblanchon/ArduinoJson@^5",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(LibraryPackageManager().get_installed()) == [
        PackageSpec("ArduinoJson@5.13.4"),
        PackageSpec("DallasTemperature@3.9.0+sha.964939d"),
        PackageSpec("OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")),
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
            "bblanchon/ArduinoJson@^5",
        ],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(LibraryPackageManager(storage_dir).get_installed()) == [
        PackageSpec("ArduinoJson@5.13.4")
    ]

    # tools
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-t", "platformio/framework-arduino-avr-attiny@^1.5.2"],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
        PackageSpec("framework-arduino-avr-attiny@1.5.2")
    ]

    # platforms
    result = clirunner.invoke(
        package_install_cmd,
        ["--global", "-p", "platformio/atmelavr@^3.4.0", "--skip-dependencies"],
    )
    validate_cliresult(result)
    assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
        PackageSpec("atmelavr@3.4.0")
    ]


def test_skip_dependencies(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
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
        assert pkgs_to_specs(installed_lib_pkgs) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec("ESPAsyncWebServer-esphome@2.1.0"),
        ]
        assert len(ToolPackageManager().get_installed()) == 1  # SCons


def test_baremetal_project(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
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
        assert pkgs_to_specs(installed_lib_pkgs) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec("ESPAsyncWebServer-esphome@2.1.0"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("tool-scons@%s" % get_core_dependencies()["tool-scons"][1:]),
            PackageSpec("toolchain-atmelavr@1.70300.191015"),
        ]


def test_project(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
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
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec("ESPAsyncWebServer-esphome@2.1.0"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("framework-arduino-avr-attiny@1.5.2"),
            PackageSpec("tool-scons@%s" % get_core_dependencies()["tool-scons"][1:]),
            PackageSpec("toolchain-atmelavr@1.70300.191015"),
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "milesburton/DallasTemperature@^3.9.1",
            "https://github.com/esphome/ESPAsyncWebServer/archive/refs/tags/v2.1.0.zip",
        ]

    # test "Already up-to-date"
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir)],
    )
    validate_cliresult(result)
    assert "Already up-to-date" in result.output


def test_private_lib_deps(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
    project_dir = tmp_path / "project"
    private_lib_dir = project_dir / "lib" / "private"
    private_lib_dir.mkdir(parents=True)
    (private_lib_dir / "library.json").write_text(
        """
{
    "name": "My Private Lib",
    "version": "1.0.0",
    "dependencies": {
        "bblanchon/ArduinoJson": "^5",
        "milesburton/DallasTemperature": "^3.9.1"
    }
}
"""
    )
    (project_dir / "platformio.ini").write_text(
        """
[env:private]
platform = native
"""
    )
    with fs.cd(str(project_dir)):
        config = ProjectConfig()

        # some deps were added by user manually
        result = clirunner.invoke(
            package_install_cmd,
            [
                "-g",
                "--storage-dir",
                config.get("platformio", "lib_dir"),
                "-l",
                "paulstoffregen/OneWire@^2.3.5",
            ],
        )
        validate_cliresult(result)

        # ensure all deps are installed
        result = clirunner.invoke(package_install_cmd)
        validate_cliresult(result)
        installed_private_pkgs = LibraryPackageManager(
            config.get("platformio", "lib_dir")
        ).get_installed()
        assert pkgs_to_specs(installed_private_pkgs) == [
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
            PackageSpec("My Private Lib@1.0.0"),
        ]
        installed_env_pkgs = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "private")
        ).get_installed()
        assert pkgs_to_specs(installed_env_pkgs) == [
            PackageSpec("ArduinoJson@5.13.4"),
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
        ]


def test_remove_project_unused_libdeps(
    clirunner, validate_cliresult, isolated_pio_core, get_pkg_latest_version, tmp_path
):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    result = clirunner.invoke(
        package_install_cmd,
        ["-d", str(project_dir), "-e", "baremetal"],
    )
    validate_cliresult(result)
    with fs.cd(str(project_dir)):
        config = ProjectConfig()
        storage_dir = os.path.join(config.get("platformio", "libdeps_dir"), "baremetal")
        lm = LibraryPackageManager(storage_dir)
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec("ESPAsyncWebServer-esphome@2.1.0"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]

        # add new deps
        lib_deps = config.get("env:baremetal", "lib_deps")
        config.set("env:baremetal", "lib_deps", lib_deps + ["bblanchon/ArduinoJson@^5"])
        config.save()
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "baremetal"],
        )
        validate_cliresult(result)
        lm = LibraryPackageManager(storage_dir)
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec("ArduinoJson@5.13.4"),
            PackageSpec(
                "DallasTemperature@%s"
                % get_pkg_latest_version("milesburton/DallasTemperature")
            ),
            PackageSpec("ESPAsyncWebServer-esphome@2.1.0"),
            PackageSpec(
                "OneWire@%s" % get_pkg_latest_version("paulstoffregen/OneWire")
            ),
        ]

        # manually remove from cofiguration file
        config.set("env:baremetal", "lib_deps", ["bblanchon/ArduinoJson@^5"])
        config.save()
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "baremetal"],
        )
        validate_cliresult(result)
        lm = LibraryPackageManager(storage_dir)
        assert pkgs_to_specs(lm.get_installed()) == [PackageSpec("ArduinoJson@5.13.4")]


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
    spec = "bblanchon/ArduinoJson@^5"
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
        assert pkgs_to_specs(lm.get_installed()) == [PackageSpec("ArduinoJson@5.13.4")]
        # do not expect any platforms/tools
        assert not os.path.exists(config.get("platformio", "platforms_dir"))
        assert not os.path.exists(config.get("platformio", "packages_dir"))

        # check saved deps
        assert config.get("env:devkit", "lib_deps") == [
            "bblanchon/ArduinoJson@^5",
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
        assert pkgs_to_specs(lm.get_installed()) == [
            PackageSpec("ArduinoJson@5.13.4"),
            PackageSpec("Nanopb@0.4.91"),
        ]
        assert config.get("env:devkit", "lib_deps") == [
            "bblanchon/ArduinoJson@^5",
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
    spec = "platformio/tool-openocd @ ^2"
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
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("tool-openocd@2.1100.211028")
        ]
        assert not LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), "devkit")
        ).get_installed()
        # do not expect any platforms
        assert not os.path.exists(config.get("platformio", "platforms_dir"))

        # check saved deps
        assert config.get("env:devkit", "platform_packages") == [
            "platformio/tool-openocd@^2",
        ]

        # install tool without saving to config
        result = clirunner.invoke(
            package_install_cmd,
            ["-e", "devkit", "-t", "platformio/tool-esptoolpy@1.20310.0", "--no-save"],
        )
        validate_cliresult(result)
        config = ProjectConfig()
        assert pkgs_to_specs(ToolPackageManager().get_installed()) == [
            PackageSpec("tool-esptoolpy@1.20310.0"),
            PackageSpec("tool-openocd@2.1100.211028"),
        ]
        assert config.get("env:devkit", "platform_packages") == [
            "platformio/tool-openocd@^2",
        ]

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
    spec = "atmelavr@^3.4.0"
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
        assert pkgs_to_specs(PlatformPackageManager().get_installed()) == [
            PackageSpec("atmelavr@3.4.0")
        ]
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
