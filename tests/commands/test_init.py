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
from os import getcwd, makedirs
from os.path import getsize, isdir, isfile, join

from platformio import util
from platformio.commands.boards import cli as cmd_boards
from platformio.commands.init import cli


def validate_pioproject(pioproject_dir):
    pioconf_path = join(pioproject_dir, "platformio.ini")
    assert isfile(pioconf_path) and getsize(pioconf_path) > 0
    assert isdir(join(pioproject_dir, "src")) and isdir(
        join(pioproject_dir, "lib"))


def test_init_default(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli)
        validate_cliresult(result)
        validate_pioproject(getcwd())


def test_init_ext_folder(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        ext_folder_name = "ext_folder"
        makedirs(ext_folder_name)
        result = clirunner.invoke(cli, ["-d", ext_folder_name])
        validate_cliresult(result)
        validate_pioproject(join(getcwd(), ext_folder_name))


def test_init_ide_eclipse(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli, ["-b", "uno", "--ide", "eclipse"])
        validate_cliresult(result)
        validate_pioproject(getcwd())
        assert all([isfile(f) for f in (".cproject", ".project")])


def test_init_special_board(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli, ["-b", "uno"])
        validate_cliresult(result)
        validate_pioproject(getcwd())

        result = clirunner.invoke(cmd_boards, ["Arduino Uno", "--json-output"])
        validate_cliresult(result)
        boards = json.loads(result.output)

        config = util.load_project_config()
        expected_result = [
            ("platform", str(boards[0]['platform'])),
            ("framework", str(boards[0]['frameworks'][0])),
            ("board", "uno")
        ]

        assert config.has_section("env:uno")
        assert len(set(expected_result).symmetric_difference(
            set(config.items("env:uno")))) == 0


def test_init_enable_auto_uploading(platformio_setup, clirunner,
                                    validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli,
                                  ["-b", "uno", "--enable-auto-uploading"])
        validate_cliresult(result)
        validate_pioproject(getcwd())
        config = util.load_project_config()
        expected_result = [
            ("platform", "atmelavr"),
            ("framework", "arduino"),
            ("board", "uno"),
            ("targets", "upload")
        ]
        assert config.has_section("env:uno")
        assert len(set(expected_result).symmetric_difference(
            set(config.items("env:uno")))) == 0


def test_init_incorrect_board(clirunner):
    result = clirunner.invoke(cli, ["-b", "missed_board"])
    assert result.exit_code == 2
    assert 'Error: Invalid value for "-b" / "--board' in result.output
    assert isinstance(result.exception, SystemExit)
