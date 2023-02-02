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
from platformio.package.commands.install import package_install_cmd


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


def test_ci_keep_build_dir_single_src_dir(
    clirunner, tmpdir_factory, validate_cliresult
):
    build_dir = str(tmpdir_factory.mktemp("ci_build_dir"))

    # Run two times to detect possible "AlreadyExists" errors
    for _ in range(2):
        result = clirunner.invoke(
            cmd_ci,
            [
                join("examples", "wiring-blink", "src"),
                "-b",
                "uno",
                "--build-dir",
                build_dir,
                "--keep-build-dir",
            ],
        )
        validate_cliresult(result)


def test_ci_keep_build_dir_nested_src_dirs(
    clirunner, tmpdir_factory, validate_cliresult
):
    build_dir = str(tmpdir_factory.mktemp("ci_build_dir"))

    # Split default Arduino project in two parts
    src_dir1 = tmpdir_factory.mktemp("src_1")
    src_dir1.join("src1.cpp").write(
        """
#include <Arduino.h>
void setup() {}
"""
    )

    src_dir2 = tmpdir_factory.mktemp("src_2")
    src_dir2.join("src2.cpp").write(
        """
#include <Arduino.h>
void loop() {}
"""
    )

    src_dir1 = str(src_dir1)
    src_dir2 = str(src_dir2)

    # Run two times to detect possible "AlreadyExists" errors
    for _ in range(2):
        result = clirunner.invoke(
            cmd_ci,
            [
                src_dir1,
                src_dir2,
                "-b",
                "teensy40",
                "--build-dir",
                build_dir,
                "--keep-build-dir",
            ],
        )

        validate_cliresult(result)


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
        package_install_cmd,
        ["--global", "--storage-dir", storage_dir, "--library", "1"],
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
                "DS2408_Switch.ino",
            ),
            "-l",
            join(storage_dir, "OneWire"),
            "-b",
            "uno",
        ],
    )
    validate_cliresult(result)
