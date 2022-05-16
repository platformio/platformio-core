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
import os

from platformio.commands.boards import cli as cmd_boards
from platformio.package.commands.exec import package_exec_cmd
from platformio.project.commands.init import project_init_cmd
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectEnvsNotAvailableError


def validate_pioproject(pioproject_dir):
    pioconf_path = os.path.join(pioproject_dir, "platformio.ini")
    assert os.path.isfile(pioconf_path) and os.path.getsize(pioconf_path) > 0
    assert os.path.isdir(os.path.join(pioproject_dir, "src")) and os.path.isdir(
        os.path.join(pioproject_dir, "lib")
    )


def test_init_default(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(project_init_cmd)
        validate_cliresult(result)
        validate_pioproject(os.getcwd())


def test_init_ext_folder(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        ext_folder_name = "ext_folder"
        os.makedirs(ext_folder_name)
        result = clirunner.invoke(project_init_cmd, ["-d", ext_folder_name])
        validate_cliresult(result)
        validate_pioproject(os.path.join(os.getcwd(), ext_folder_name))


def test_init_duplicated_boards(clirunner, validate_cliresult, tmpdir):
    with tmpdir.as_cwd():
        for _ in range(2):
            result = clirunner.invoke(
                project_init_cmd,
                ["-b", "uno", "-b", "uno", "--no-install-dependencies"],
            )
            validate_cliresult(result)
            validate_pioproject(str(tmpdir))
        config = ProjectConfig(os.path.join(os.getcwd(), "platformio.ini"))
        config.validate()
        assert set(config.sections()) == set(["env:uno"])


def test_init_ide_without_board(clirunner, tmpdir):
    with tmpdir.as_cwd():
        result = clirunner.invoke(project_init_cmd, ["--ide", "atom"])
        assert result.exit_code != 0
        assert isinstance(result.exception, ProjectEnvsNotAvailableError)


def test_init_ide_vscode(clirunner, validate_cliresult, tmpdir):
    with tmpdir.as_cwd():
        result = clirunner.invoke(
            project_init_cmd,
            [
                "--ide",
                "vscode",
                "-b",
                "uno",
                "-b",
                "teensy31",
                "--no-install-dependencies",
            ],
        )
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert all(
            tmpdir.join(".vscode").join(f).check()
            for f in ("c_cpp_properties.json", "launch.json")
        )
        assert (
            "framework-arduino-avr"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to NodeMCU
        result = clirunner.invoke(
            project_init_cmd,
            ["--ide", "vscode", "-b", "nodemcuv2", "--no-install-dependencies"],
        )
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduinoespressif8266"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to teensy31 via env name
        result = clirunner.invoke(
            project_init_cmd,
            ["--ide", "vscode", "-e", "teensy31", "--no-install-dependencies"],
        )
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduinoteensy"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to the first board
        result = clirunner.invoke(
            project_init_cmd, ["--ide", "vscode", "--no-install-dependencies"]
        )
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduino-avr"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )


def test_init_ide_eclipse(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(
            project_init_cmd,
            ["-b", "uno", "--ide", "eclipse", "--no-install-dependencies"],
        )
        validate_cliresult(result)
        validate_pioproject(os.getcwd())
        assert all(os.path.isfile(f) for f in (".cproject", ".project"))


def test_init_special_board(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(project_init_cmd, ["-b", "uno"])
        validate_cliresult(result)
        validate_pioproject(os.getcwd())

        result = clirunner.invoke(cmd_boards, ["Arduino Uno", "--json-output"])
        validate_cliresult(result)
        boards = json.loads(result.output)

        config = ProjectConfig(os.path.join(os.getcwd(), "platformio.ini"))
        config.validate()

        expected_result = dict(
            platform=str(boards[0]["platform"]),
            board="uno",
            framework=[str(boards[0]["frameworks"][0])],
        )
        assert config.has_section("env:uno")
        assert sorted(config.items(env="uno", as_dict=True).items()) == sorted(
            expected_result.items()
        )


def test_init_enable_auto_uploading(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(
            project_init_cmd,
            [
                "-b",
                "uno",
                "--project-option",
                "targets=upload",
                "--no-install-dependencies",
            ],
        )
        validate_cliresult(result)
        validate_pioproject(os.getcwd())
        config = ProjectConfig(os.path.join(os.getcwd(), "platformio.ini"))
        config.validate()
        expected_result = dict(
            targets=["upload"], platform="atmelavr", board="uno", framework=["arduino"]
        )
        assert config.has_section("env:uno")
        assert sorted(config.items(env="uno", as_dict=True).items()) == sorted(
            expected_result.items()
        )


def test_init_custom_framework(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(
            project_init_cmd,
            [
                "-b",
                "teensy31",
                "--project-option",
                "framework=mbed",
                "--no-install-dependencies",
            ],
        )
        validate_cliresult(result)
        validate_pioproject(os.getcwd())
        config = ProjectConfig(os.path.join(os.getcwd(), "platformio.ini"))
        config.validate()
        expected_result = dict(platform="teensy", board="teensy31", framework=["mbed"])
        assert config.has_section("env:teensy31")
        assert sorted(config.items(env="teensy31", as_dict=True).items()) == sorted(
            expected_result.items()
        )


def test_init_incorrect_board(clirunner):
    result = clirunner.invoke(project_init_cmd, ["-b", "missed_board"])
    assert result.exit_code == 2
    assert "Error: Invalid value for" in result.output
    assert isinstance(result.exception, SystemExit)


def test_init_ide_clion(clirunner, validate_cliresult, tmpdir):
    project_dir = tmpdir.join("project").mkdir()
    # Add extra libraries to cover cases with possible unwanted backslashes
    lib_extra_dirs = tmpdir.join("extra_libs").mkdir()
    extra_lib = lib_extra_dirs.join("extra_lib").mkdir()
    extra_lib.join("extra_lib.h").write(" ")
    extra_lib.join("extra_lib.cpp").write(" ")

    with project_dir.as_cwd():
        result = clirunner.invoke(
            project_init_cmd,
            [
                "-b",
                "uno",
                "--ide",
                "clion",
                "--project-option",
                "framework=arduino",
                "--project-option",
                "platform_packages=platformio/tool-ninja",
                "--project-option",
                "lib_extra_dirs=%s" % str(lib_extra_dirs),
            ],
        )

        validate_cliresult(result)
        assert all(
            os.path.isfile(f) for f in ("CMakeLists.txt", "CMakeListsPrivate.txt")
        )

        project_dir.join("src").join("main.cpp").write(
            """#include <Arduino.h>
#include "extra_lib.h"
void setup(){}
void loop(){}
"""
        )
        project_dir.join("build_dir").mkdir()
        result = clirunner.invoke(
            package_exec_cmd,
            [
                "-p",
                "tool-cmake",
                "--",
                "cmake",
                "-DCMAKE_BUILD_TYPE=uno",
                "-DCMAKE_MAKE_PROGRAM=%s"
                % os.path.join(
                    ProjectConfig().get("platformio", "packages_dir"),
                    "tool-ninja",
                    "ninja",
                ),
                "-G",
                "Ninja",
                "-S",
                str(project_dir),
                "-B",
                "build_dir",
            ],
        )
        validate_cliresult(result)

        # build
        result = clirunner.invoke(
            package_exec_cmd,
            [
                "-p",
                "tool-cmake",
                "--",
                "cmake",
                "--build",
                "build_dir",
                "--target",
                "Debug",
            ],
        )
        validate_cliresult(result)
