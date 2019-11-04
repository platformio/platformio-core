# Copyright (c) 2019-present PlatformIO <contact@platformio.org>
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
from os.path import isfile, join

import pytest

from platformio.commands.check.command import cli as cmd_check

DEFAULT_CONFIG = """
[env:native]
platform = native
"""

TEST_CODE = """
#include <stdlib.h>

void run_defects() {
    /* Freeing a pointer twice */
    int* doubleFreePi = (int*)malloc(sizeof(int));
    *doubleFreePi=2;
    free(doubleFreePi);
    free(doubleFreePi); /* High */

    /* Reading uninitialized memory */
    int* uninitializedPi = (int*)malloc(sizeof(int));
    *uninitializedPi++; /* High + Medium*/
    free(uninitializedPi);

    /* Delete instead of delete [] */
    int* wrongDeletePi = new int[10];
    wrongDeletePi++;
    delete wrongDeletePi; /* High */

    /* Index out of bounds */
    int arr[10];
    for(int i=0; i < 11; i++) {
        arr[i] = 0; /* High */
    }
}

int main() {
    int uninitializedVar; /* Low */
    run_defects();
}
"""

EXPECTED_ERRORS = 4
EXPECTED_WARNINGS = 1
EXPECTED_STYLE = 1
EXPECTED_DEFECTS = EXPECTED_ERRORS + EXPECTED_WARNINGS + EXPECTED_STYLE


@pytest.fixture(scope="module")
def check_dir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    return tmpdir


def count_defects(output):
    error, warning, style = 0, 0, 0
    for l in output.split("\n"):
        if "[high:error]" in l:
            error += 1
        elif "[medium:warning]" in l:
            warning += 1
        elif "[low:style]" in l:
            style += 1
    return error, warning, style


def test_check_cli_output(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir)])

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors + warnings + style == EXPECTED_DEFECTS


def test_check_json_output(clirunner, check_dir):
    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), "--json-output"]
    )
    output = json.loads(result.stdout.strip())

    assert isinstance(output, list)
    assert len(output[0].get("defects", [])) == EXPECTED_DEFECTS


def test_check_tool_defines_passed(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--verbose"])
    output = result.output

    assert "PLATFORMIO=" in output
    assert "__GNUC__" in output


def test_check_severity_threshold(clirunner, check_dir):
    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), "--severity=high"]
    )

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors == EXPECTED_ERRORS
    assert warnings == 0
    assert style == 0


def test_check_includes_passed(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--verbose"])
    output = result.output

    inc_count = 0
    for l in output.split("\n"):
        if l.startswith("Includes:"):
            inc_count = l.count("-I")

    # at least 1 include path for default mode
    assert inc_count > 1


def test_check_silent_mode(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--silent"])

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors == EXPECTED_ERRORS
    assert warnings == 0
    assert style == 0


def test_check_custom_pattern_absolute_path(clirunner, tmpdir_factory):
    project_dir = tmpdir_factory.mktemp("project")
    project_dir.join("platformio.ini").write(DEFAULT_CONFIG)

    check_dir = tmpdir_factory.mktemp("custom_src_dir")
    check_dir.join("main.cpp").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(project_dir), "--pattern=" + str(check_dir)]
    )

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors == EXPECTED_ERRORS
    assert warnings == EXPECTED_WARNINGS
    assert style == EXPECTED_STYLE


def test_check_custom_pattern_relative_path(clirunner, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)

    tmpdir.mkdir("app").join("main.cpp").write(TEST_CODE)
    tmpdir.mkdir("prj").join("test.cpp").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--pattern=app", "--pattern=prj"]
    )

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors + warnings + style == EXPECTED_DEFECTS * 2


def test_check_no_source_files(clirunner, tmpdir):
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)
    tmpdir.mkdir("src")

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code != 0
    assert errors == 0
    assert warnings == 0
    assert style == 0


def test_check_bad_flag_passed(clirunner, check_dir):
    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), '"--flags=--UNKNOWN"']
    )

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code != 0
    assert errors == 0
    assert warnings == 0
    assert style == 0


def test_check_success_if_no_errors(clirunner, tmpdir):
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)
    tmpdir.mkdir("src").join("main.c").write(
        """
#include <stdlib.h>

void unused_function(){
    int unusedVar = 0;
    int* iP = &unusedVar;
    *iP++;
}

int main() {
}
"""
    )

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])

    errors, warnings, style = count_defects(result.output)

    assert "[PASSED]" in result.output
    assert result.exit_code == 0
    assert errors == 0
    assert warnings == 1
    assert style == 1


def test_check_individual_flags_passed(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy"
    config += "\ncheck_flags = cppcheck: --std=c++11 \n\tclangtidy: --fix-errors"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    clang_flags_found = cppcheck_flags_found = False
    for l in result.output.split("\n"):
        if "--fix" in l and "clang-tidy" in l and "--std=c++11" not in l:
            clang_flags_found = True
        elif "--std=c++11" in l and "cppcheck" in l and "--fix" not in l:
            cppcheck_flags_found = True

    assert clang_flags_found
    assert cppcheck_flags_found


def test_check_cppcheck_misra_addon(clirunner, check_dir):
    check_dir.join("misra.json").write(
        """
{
    "script": "addons/misra.py",
    "args": ["--rule-texts=rules.txt"]
}
"""
    )

    check_dir.join("rules.txt").write(
        """
Appendix A Summary of guidelines
Rule 3.1 Required
R3.1 text.
Rule 4.1 Required
R4.1 text.
Rule 10.4 Mandatory
R10.4 text.
Rule 11.5 Advisory
R11.5 text.
Rule 15.5 Advisory
R15.5 text.
Rule 15.6 Required
R15.6 text.
Rule 17.7 Required
R17.7 text.
Rule 20.1 Advisory
R20.1 text.
Rule 21.3 Required
R21.3 Found MISRA defect
Rule 21.4
R21.4 text.
"""
    )

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), "--flags=--addon=misra.json"]
    )

    assert result.exit_code == 0
    assert "R21.3 Found MISRA defect" in result.output
    assert not isfile(join(str(check_dir), "src", "main.cpp.dump"))


def test_check_fails_on_defects_only_with_flag(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])

    result_with_flag = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=high"]
    )

    assert default_result.exit_code == 0
    assert result_with_flag.exit_code != 0


def test_check_fails_on_defects_only_on_specified_level(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(
        """
#include <stdlib.h>

void unused_function(){
    int unusedVar = 0;
    int* iP = &unusedVar;
    *iP++;
}

int main() {
}
"""
    )

    high_result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=high"]
    )

    low_result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=low"]
    )

    assert high_result.exit_code == 0
    assert low_result.exit_code != 0

