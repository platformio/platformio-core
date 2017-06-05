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

from os.path import join

from platformio.commands.ci import cli as cmd_ci


def test_ci_empty(clirunner):
    result = clirunner.invoke(cmd_ci)
    assert result.exit_code == 2
    assert "Invalid value: Missing argument 'src'" in result.output


def test_ci_boards(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_ci, [
        join("examples", "atmelavr-and-arduino", "arduino-internal-libs",
             "src", "ChatServer.ino"), "-b", "uno", "-b", "leonardo"
    ])
    validate_cliresult(result)


def test_ci_project_conf(clirunner, validate_cliresult):
    project_dir = join("examples", "atmelavr-and-arduino",
                       "arduino-internal-libs")
    result = clirunner.invoke(cmd_ci, [
        join(project_dir, "src", "ChatServer.ino"), "--project-conf",
        join(project_dir, "platformio.ini")
    ])
    validate_cliresult(result)
    assert all([s in result.output for s in ("ethernet", "leonardo", "yun")])


def test_ci_lib_and_board(clirunner, validate_cliresult):
    example_dir = join("examples", "atmelavr-and-arduino",
                       "arduino-external-libs")
    result = clirunner.invoke(cmd_ci, [
        join(example_dir, "lib", "OneWire", "examples", "DS2408_Switch",
             "DS2408_Switch.pde"), "-l", join(example_dir, "lib", "OneWire"),
        "-b", "uno"
    ])
    validate_cliresult(result)
