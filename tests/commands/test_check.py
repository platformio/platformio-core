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

# pylint: disable=redefined-outer-name

import json
import os
import sys

import pytest

from platformio import fs
from platformio.check.cli import cli as cmd_check

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


PVS_STUDIO_FREE_LICENSE_HEADER = """
// This is an open source non-commercial project. Dear PVS-Studio, please check it.
// PVS-Studio Static Code Analyzer for C, C++, C#, and Java: http://www.viva64.com
"""

EXPECTED_ERRORS = 5
EXPECTED_WARNINGS = 1
EXPECTED_STYLE = 4
EXPECTED_DEFECTS = EXPECTED_ERRORS + EXPECTED_WARNINGS + EXPECTED_STYLE


@pytest.fixture(scope="module")
def check_dir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    return tmpdir


def count_defects(output):
    error, warning, style = 0, 0, 0
    for line in output.split("\n"):
        if "[high:error]" in line:
            error += 1
        elif "[medium:warning]" in line:
            warning += 1
        elif "[low:style]" in line:
            style += 1
    return error, warning, style


def test_check_cli_output(clirunner, validate_cliresult, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir)])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS


def test_check_json_output(clirunner, validate_cliresult, check_dir):
    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), "--json-output"]
    )
    validate_cliresult(result)

    output = json.loads(result.stdout.strip())

    assert isinstance(output, list)
    assert len(output[0].get("defects", [])) == EXPECTED_DEFECTS


def test_check_tool_defines_passed(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--verbose"])
    output = result.output

    assert "PLATFORMIO=" in output
    assert "__GNUC__" in output


def test_check_tool_complex_defines_handled(
    clirunner, validate_cliresult, tmpdir_factory
):
    project_dir = tmpdir_factory.mktemp("project_dir")

    project_dir.join("platformio.ini").write(
        DEFAULT_CONFIG
        + R"""
check_tool = cppcheck, clangtidy, pvs-studio
build_flags =
    -DEXTERNAL_INCLUDE_FILE=\"test.h\"
    "-DDEFINE_WITH_SPACE="Hello World!""
"""
    )

    src_dir = project_dir.mkdir("src")
    src_dir.join("test.h").write(
        """
#ifndef TEST_H
#define TEST_H
#define ARBITRARY_CONST_VALUE 10
#endif
"""
    )

    src_dir.join("main.c").write(
        PVS_STUDIO_FREE_LICENSE_HEADER
        + """
#if !defined(EXTERNAL_INCLUDE_FILE)
#error "EXTERNAL_INCLUDE_FILE is not declared!"
#else
#include EXTERNAL_INCLUDE_FILE
#endif

int main()
{
    /* Index out of bounds */
    int arr[ARBITRARY_CONST_VALUE];
    for(int i=0; i < ARBITRARY_CONST_VALUE+1; i++) {
        arr[i] = 0; /* High */
    }
    return 0;
}
"""
    )

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(project_dir)])
    validate_cliresult(default_result)


def test_check_language_standard_definition_passed(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\nbuild_flags = -std=c++17"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert "__cplusplus=201703L" in result.output
    assert "--std=c++17" in result.output


def test_check_language_standard_option_is_converted(clirunner, tmpdir):
    config = (
        DEFAULT_CONFIG
        + """
build_flags = -std=gnu++1y
    """
    )
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert "--std=c++14" in result.output


def test_check_language_standard_is_prioritized_over_build_flags(clirunner, tmpdir):
    config = (
        DEFAULT_CONFIG
        + """
check_flags = --std=c++03
build_flags = -std=c++17
    """
    )
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert "--std=c++03" in result.output
    assert "--std=c++17" not in result.output


def test_check_language_standard_for_c_language(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\nbuild_flags = -std=c11"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(TEST_CODE)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert "--std=c11" in result.output
    assert "__STDC_VERSION__=201112L" in result.output
    assert "__cplusplus" not in result.output


def test_check_severity_threshold(clirunner, validate_cliresult, check_dir):
    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(check_dir), "--severity=high"]
    )
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors == EXPECTED_ERRORS
    assert warnings == 0
    assert style == 0


def test_check_includes_passed(clirunner, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--verbose"])

    inc_count = 0
    for line in result.output.split("\n"):
        if line.startswith("Includes:"):
            inc_count = line.count("-I")

    # at least 1 include path for default mode
    assert inc_count > 0


def test_check_silent_mode(clirunner, validate_cliresult, check_dir):
    result = clirunner.invoke(cmd_check, ["--project-dir", str(check_dir), "--silent"])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors == EXPECTED_ERRORS
    assert warnings == 0
    assert style == 0


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


def test_check_success_if_no_errors(clirunner, validate_cliresult, tmpdir):
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
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert "[PASSED]" in result.output
    assert errors == 0
    assert warnings == 1
    assert style == 1


def test_check_individual_flags_passed(clirunner, validate_cliresult, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy, pvs-studio"
    config += """\ncheck_flags =
    cppcheck: --std=c++11
    clangtidy: --fix-errors
    pvs-studio: --analysis-mode=4
"""

    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(
        PVS_STUDIO_FREE_LICENSE_HEADER + TEST_CODE
    )
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])
    validate_cliresult(result)

    clang_flags_found = cppcheck_flags_found = pvs_flags_found = False
    for l in result.output.split("\n"):
        if "--fix" in l and "clang-tidy" in l and "--std=c++11" not in l:
            clang_flags_found = True
        elif "--std=c++11" in l and "cppcheck" in l and "--fix" not in l:
            cppcheck_flags_found = True
        elif (
            "--analysis-mode=4" in l and "pvs-studio" in l.lower() and "--fix" not in l
        ):
            pvs_flags_found = True

    assert clang_flags_found
    assert cppcheck_flags_found
    assert pvs_flags_found


def test_check_cppcheck_misra_addon(clirunner, validate_cliresult, tmpdir_factory):
    check_dir = tmpdir_factory.mktemp("project")
    check_dir.join("platformio.ini").write(DEFAULT_CONFIG)
    check_dir.mkdir("src").join("main.c").write(TEST_CODE)
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

    validate_cliresult(result)
    assert "R21.3 Found MISRA defect" in result.output
    assert not os.path.isfile(os.path.join(str(check_dir), "src", "main.cpp.dump"))


def test_check_fails_on_defects_only_with_flag(clirunner, validate_cliresult, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(TEST_CODE)

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])

    result_with_flag = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=high"]
    )

    validate_cliresult(default_result)
    assert result_with_flag.exit_code != 0


def test_check_fails_on_defects_only_on_specified_level(
    clirunner, validate_cliresult, tmpdir
):
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
    validate_cliresult(high_result)

    low_result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=low"]
    )

    assert low_result.exit_code != 0


def test_check_pvs_studio_free_license(clirunner, tmpdir):
    config = """
[env:test]
platform = teensy
board = teensy35
framework = arduino
check_tool = pvs-studio
"""

    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(PVS_STUDIO_FREE_LICENSE_HEADER + TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--fail-on-defect=high", "-v"]
    )

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code != 0
    assert errors != 0
    assert warnings != 0
    assert style == 0


def test_check_pvs_studio_fails_without_license(clirunner, tmpdir):
    config = DEFAULT_CONFIG + "\ncheck_tool = pvs-studio"

    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(TEST_CODE)

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    verbose_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert default_result.exit_code != 0
    assert "failed to perform check" in default_result.output.lower()

    assert verbose_result.exit_code != 0
    assert "license was not entered" in verbose_result.output.lower()


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="For some reason the error message is different on Windows",
)
def test_check_pvs_studio_fails_broken_license(clirunner, tmpdir):
    config = (
        DEFAULT_CONFIG
        + """
check_tool = pvs-studio
check_flags = --lic-file=./pvs-studio.lic
"""
    )

    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(TEST_CODE)
    tmpdir.join("pvs-studio.lic").write(
        """
TEST
TEST-TEST-TEST-TEST
"""
    )

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    verbose_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir), "-v"])

    assert default_result.exit_code != 0
    assert "failed to perform check" in default_result.output.lower()

    assert verbose_result.exit_code != 0
    assert "license information is incorrect" in verbose_result.output.lower()


@pytest.mark.parametrize("framework", ["arduino", "stm32cube", "zephyr"])
@pytest.mark.parametrize("check_tool", ["cppcheck", "clangtidy", "pvs-studio"])
def test_check_embedded_platform_all_tools(
    clirunner, validate_cliresult, tmpdir, framework, check_tool
):
    config = f"""
[env:test]
platform = ststm32
board = nucleo_f401re
framework = {framework}
check_tool = {check_tool}
"""
    tmpdir.mkdir("src").join("main.c").write(
        PVS_STUDIO_FREE_LICENSE_HEADER
        + """
#include <stdlib.h>

void unused_function(int val){
    int unusedVar = 0;
    int* iP = &unusedVar;
    *iP++;
}

int main() {
}
"""
    )

    if framework == "zephyr":
        zephyr_dir = tmpdir.mkdir("zephyr")
        zephyr_dir.join("prj.conf").write("# nothing here")
        zephyr_dir.join("CMakeLists.txt").write(
            """cmake_minimum_required(VERSION 3.16.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(hello_world)
target_sources(app PRIVATE ../src/main.c)"""
        )

    tmpdir.join("platformio.ini").write(config)
    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    validate_cliresult(result)
    defects = sum(count_defects(result.output))
    assert defects > 0, "Not defects were found!"


def test_check_skip_includes_from_packages(clirunner, validate_cliresult, tmpdir):
    config = """
[env:test]
platform = nordicnrf52
board = nrf52_dk
framework = arduino
"""

    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.c").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "--skip-packages", "-v"]
    )
    validate_cliresult(result)

    project_path = fs.to_unix_path(str(tmpdir))
    for line in result.output.split("\n"):
        if not line.startswith("Includes:"):
            continue
        for inc in line.split(" "):
            if inc.startswith("-I") and project_path not in inc:
                pytest.fail("Detected an include path from packages: " + inc)


def test_check_multiline_error(clirunner, tmpdir_factory):
    project_dir = tmpdir_factory.mktemp("project")
    project_dir.join("platformio.ini").write(DEFAULT_CONFIG)

    project_dir.mkdir("include").join("main.h").write(
        """
#error This is a multiline error message \\
that should be correctly reported \\
in both default and verbose modes.
"""
    )

    project_dir.mkdir("src").join("main.c").write(
        """
#include <stdlib.h>
#include "main.h"

int main() {}
"""
    )

    result = clirunner.invoke(cmd_check, ["--project-dir", str(project_dir)])
    errors, _, _ = count_defects(result.output)

    result = clirunner.invoke(cmd_check, ["--project-dir", str(project_dir), "-v"])
    verbose_errors, _, _ = count_defects(result.output)

    assert verbose_errors == errors == 1


def test_check_handles_spaces_in_paths(clirunner, validate_cliresult, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project dir")
    config = DEFAULT_CONFIG + "\ncheck_tool = cppcheck, clangtidy, pvs-studio"
    tmpdir.join("platformio.ini").write(config)
    tmpdir.mkdir("src").join("main.cpp").write(
        PVS_STUDIO_FREE_LICENSE_HEADER + TEST_CODE
    )

    default_result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])

    validate_cliresult(default_result)


#
# Files filtering functionality
#


@pytest.mark.parametrize(
    "src_filter,number_of_checked_files",
    [
        (["+<src/app.cpp>"], 1),
        (["+<tests/*.cpp>"], 1),
        (["+<src>", "-<src/*.cpp>"], 2),
        (["-<*> +<src/main.cpp> +<src/uart/uart.cpp> +<src/spi/spi.cpp>"], 3),
    ],
    ids=["Single file", "Glob pattern", "Exclude pattern", "Filter as string"],
)
def test_check_src_filter(
    clirunner,
    validate_cliresult,
    tmpdir_factory,
    src_filter,
    number_of_checked_files,
):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)

    src_dir = tmpdir.mkdir("src")
    src_dir.join("main.cpp").write(TEST_CODE)
    src_dir.join("app.cpp").write(TEST_CODE)
    src_dir.mkdir("uart").join("uart.cpp").write(TEST_CODE)
    src_dir.mkdir("spi").join("spi.cpp").write(TEST_CODE)
    tmpdir.mkdir("tests").join("test.cpp").write(TEST_CODE)

    cmd_args = ["--project-dir", str(tmpdir)] + [
        "--src-filters=%s" % f for f in src_filter
    ]

    result = clirunner.invoke(cmd_check, cmd_args)
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS * number_of_checked_files


def test_check_src_filter_from_config(clirunner, validate_cliresult, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")

    config = (
        DEFAULT_CONFIG
        + """
check_src_filters =
    +<src/spi/*.c*>
    +<tests/test.cpp>
    """
    )
    tmpdir.join("platformio.ini").write(config)

    src_dir = tmpdir.mkdir("src")
    src_dir.join("main.cpp").write(TEST_CODE)
    src_dir.mkdir("spi").join("spi.cpp").write(TEST_CODE)
    tmpdir.mkdir("tests").join("test.cpp").write(TEST_CODE)

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS * 2
    assert "main.cpp" not in result.output


def test_check_custom_pattern_absolute_path_legacy(
    clirunner, validate_cliresult, tmpdir_factory
):
    project_dir = tmpdir_factory.mktemp("project")
    project_dir.join("platformio.ini").write(DEFAULT_CONFIG)

    check_dir = tmpdir_factory.mktemp("custom_src_dir")
    check_dir.join("main.cpp").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(project_dir), "--pattern=" + str(check_dir)]
    )

    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors == EXPECTED_ERRORS
    assert warnings == EXPECTED_WARNINGS
    assert style == EXPECTED_STYLE


def test_check_custom_pattern_relative_path_legacy(
    clirunner, validate_cliresult, tmpdir_factory
):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(DEFAULT_CONFIG)

    src_dir = tmpdir.mkdir("src")
    src_dir.join("main.cpp").write(TEST_CODE)
    src_dir.mkdir("uart").join("uart.cpp").write(TEST_CODE)
    src_dir.mkdir("spi").join("spi.cpp").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check,
        ["--project-dir", str(tmpdir), "--pattern=src/uart", "--pattern=src/spi"],
    )
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS * 2


def test_check_src_filter_from_config_legacy(
    clirunner, validate_cliresult, tmpdir_factory
):
    tmpdir = tmpdir_factory.mktemp("project")

    config = (
        DEFAULT_CONFIG
        + """
check_patterns =
    src/spi/*.c*
    tests/test.cpp
    """
    )
    tmpdir.join("platformio.ini").write(config)

    src_dir = tmpdir.mkdir("src")
    src_dir.join("main.cpp").write(TEST_CODE)
    src_dir.mkdir("spi").join("spi.cpp").write(TEST_CODE)
    tmpdir.mkdir("tests").join("test.cpp").write(TEST_CODE)

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS * 2
    assert "main.cpp" not in result.output


def test_check_src_filter_multiple_envs(clirunner, validate_cliresult, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")

    config = """
[env]
check_tool = cppcheck
check_src_filters =
    +<src/*>

[env:check_sources]
platform = native

[env:check_tests]
platform = native
check_src_filters =
    +<test/*>
    """
    tmpdir.join("platformio.ini").write(config)

    src_dir = tmpdir.mkdir("src")
    src_dir.join("main.cpp").write(TEST_CODE)
    src_dir.mkdir("spi").join("spi.cpp").write(TEST_CODE)
    tmpdir.mkdir("test").join("test.cpp").write(TEST_CODE)

    result = clirunner.invoke(
        cmd_check, ["--project-dir", str(tmpdir), "-e", "check_tests"]
    )
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert errors + warnings + style == EXPECTED_DEFECTS
    assert "test.cpp" in result.output
    assert "main.cpp" not in result.output


def test_check_sources_in_project_root(clirunner, validate_cliresult, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")

    config = (
        """
[platformio]
src_dir = ./
    """
        + DEFAULT_CONFIG
    )
    tmpdir.join("platformio.ini").write(config)
    tmpdir.join("main.cpp").write(TEST_CODE)
    tmpdir.mkdir("spi").join("uart.cpp").write(TEST_CODE)

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors + warnings + style == EXPECTED_DEFECTS * 2


def test_check_sources_in_external_dir(clirunner, validate_cliresult, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    external_src_dir = tmpdir_factory.mktemp("external_src_dir")

    config = (
        f"""
[platformio]
src_dir = {external_src_dir}
    """
        + DEFAULT_CONFIG
    )
    tmpdir.join("platformio.ini").write(config)
    external_src_dir.join("main.cpp").write(TEST_CODE)

    result = clirunner.invoke(cmd_check, ["--project-dir", str(tmpdir)])
    validate_cliresult(result)

    errors, warnings, style = count_defects(result.output)

    assert result.exit_code == 0
    assert errors + warnings + style == EXPECTED_DEFECTS
