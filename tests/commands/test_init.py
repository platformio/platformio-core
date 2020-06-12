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
from os import getcwd, makedirs
from os.path import getsize, isdir, isfile, join

from platformio.commands.boards import cli as cmd_boards
from platformio.commands.project import project_init as cmd_init
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectEnvsNotAvailableError


def validate_pioproject(pioproject_dir):
    pioconf_path = join(pioproject_dir, "platformio.ini")
    assert isfile(pioconf_path) and getsize(pioconf_path) > 0
    assert isdir(join(pioproject_dir, "src")) and isdir(join(pioproject_dir, "lib"))


def test_init_default(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_init)
        validate_cliresult(result)
        validate_pioproject(getcwd())


def test_init_ext_folder(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        ext_folder_name = "ext_folder"
        makedirs(ext_folder_name)
        result = clirunner.invoke(cmd_init, ["-d", ext_folder_name])
        validate_cliresult(result)
        validate_pioproject(join(getcwd(), ext_folder_name))


def test_init_duplicated_boards(clirunner, validate_cliresult, tmpdir):
    with tmpdir.as_cwd():
        for _ in range(2):
            result = clirunner.invoke(cmd_init, ["-b", "uno", "-b", "uno"])
            validate_cliresult(result)
            validate_pioproject(str(tmpdir))
        config = ProjectConfig(join(getcwd(), "platformio.ini"))
        config.validate()
        assert set(config.sections()) == set(["env:uno"])


def test_init_ide_without_board(clirunner, tmpdir):
    with tmpdir.as_cwd():
        result = clirunner.invoke(cmd_init, ["--ide", "atom"])
        assert result.exit_code != 0
        assert isinstance(result.exception, ProjectEnvsNotAvailableError)


def test_init_ide_vscode(clirunner, validate_cliresult, tmpdir):
    with tmpdir.as_cwd():
        result = clirunner.invoke(
            cmd_init, ["--ide", "vscode", "-b", "uno", "-b", "teensy31"]
        )
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert all(
            [
                tmpdir.join(".vscode").join(f).check()
                for f in ("c_cpp_properties.json", "launch.json")
            ]
        )
        assert (
            "framework-arduino-avr"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to NodeMCU
        result = clirunner.invoke(cmd_init, ["--ide", "vscode", "-b", "nodemcuv2"])
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduinoespressif8266"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to teensy31 via env name
        result = clirunner.invoke(cmd_init, ["--ide", "vscode", "-e", "teensy31"])
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduinoteensy"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )

        # switch to the first board
        result = clirunner.invoke(cmd_init, ["--ide", "vscode"])
        validate_cliresult(result)
        validate_pioproject(str(tmpdir))
        assert (
            "framework-arduino-avr"
            in tmpdir.join(".vscode").join("c_cpp_properties.json").read()
        )


def test_init_ide_eclipse(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_init, ["-b", "uno", "--ide", "eclipse"])
        validate_cliresult(result)
        validate_pioproject(getcwd())
        assert all([isfile(f) for f in (".cproject", ".project")])


def test_init_special_board(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_init, ["-b", "uno"])
        validate_cliresult(result)
        validate_pioproject(getcwd())

        result = clirunner.invoke(cmd_boards, ["Arduino Uno", "--json-output"])
        validate_cliresult(result)
        boards = json.loads(result.output)

        config = ProjectConfig(join(getcwd(), "platformio.ini"))
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
            cmd_init, ["-b", "uno", "--project-option", "targets=upload"]
        )
        validate_cliresult(result)
        validate_pioproject(getcwd())
        config = ProjectConfig(join(getcwd(), "platformio.ini"))
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
            cmd_init, ["-b", "teensy31", "--project-option", "framework=mbed"]
        )
        validate_cliresult(result)
        validate_pioproject(getcwd())
        config = ProjectConfig(join(getcwd(), "platformio.ini"))
        config.validate()
        expected_result = dict(platform="teensy", board="teensy31", framework=["mbed"])
        assert config.has_section("env:teensy31")
        assert sorted(config.items(env="teensy31", as_dict=True).items()) == sorted(
            expected_result.items()
        )


def test_init_incorrect_board(clirunner):
    result = clirunner.invoke(cmd_init, ["-b", "missed_board"])
    assert result.exit_code == 2
    assert "Error: Invalid value for" in result.output
    assert isinstance(result.exception, SystemExit)
