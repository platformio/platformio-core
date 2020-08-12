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

from os.path import isfile, join

from platformio.commands.ci import cli as cmd_ci
from platformio.commands.lib.command import cli as cmd_lib


def test_ci_empty(clirunner):
    result = clirunner.invoke(cmd_ci)
    assert result.exit_code != 0
    assert "Invalid value: Missing argument 'src'" in result.output


def test_ci_boards(clirunner, validate_cliresult):
    result = clirunner.invoke(
        cmd_ci,
        [
            join("examples", "wiring-blink", "src", "main.cpp"),
            "-b",
            "uno",
            "-b",
            "leonardo",
        ],
    )
    validate_cliresult(result)


def test_ci_build_dir(clirunner, tmpdir_factory, validate_cliresult):
    build_dir = str(tmpdir_factory.mktemp("ci_build_dir"))
    result = clirunner.invoke(
        cmd_ci,
        [
            join("examples", "wiring-blink", "src", "main.cpp"),
            "-b",
            "uno",
            "--build-dir",
            build_dir,
        ],
    )
    validate_cliresult(result)
    assert not isfile(join(build_dir, "platformio.ini"))


def test_ci_keep_build_dir(clirunner, tmpdir_factory, validate_cliresult):
    build_dir = str(tmpdir_factory.mktemp("ci_build_dir"))
    result = clirunner.invoke(
        cmd_ci,
        [
            join("examples", "wiring-blink", "src", "main.cpp"),
            "-b",
            "uno",
            "--build-dir",
            build_dir,
            "--keep-build-dir",
        ],
    )
    validate_cliresult(result)
    assert isfile(join(build_dir, "platformio.ini"))

    # 2nd attempt
    result = clirunner.invoke(
        cmd_ci,
        [
            join("examples", "wiring-blink", "src", "main.cpp"),
            "-b",
            "metro",
            "--build-dir",
            build_dir,
            "--keep-build-dir",
        ],
    )
    validate_cliresult(result)

    assert "board: uno" in result.output
    assert "board: metro" in result.output


def test_ci_project_conf(clirunner, validate_cliresult):
    project_dir = join("examples", "wiring-blink")
    result = clirunner.invoke(
        cmd_ci,
        [
            join(project_dir, "src", "main.cpp"),
            "--project-conf",
            join(project_dir, "platformio.ini"),
        ],
    )
    validate_cliresult(result)
    assert "uno" in result.output


def test_ci_lib_and_board(clirunner, tmpdir_factory, validate_cliresult):
    storage_dir = str(tmpdir_factory.mktemp("lib"))
    result = clirunner.invoke(
        cmd_lib, ["--storage-dir", storage_dir, "install", "1@2.3.2"]
    )
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_ci,
        [
            join(
                storage_dir,
                "OneWire",
                "examples",
                "DS2408_Switch",
                "DS2408_Switch.pde",
            ),
            "-l",
            join(storage_dir, "OneWire"),
            "-b",
            "uno",
        ],
    )
    validate_cliresult(result)
