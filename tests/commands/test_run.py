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

from pathlib import Path

from platformio.run.cli import cli as cmd_run


def test_generic_build(clirunner, validate_cliresult, tmpdir):
    build_flags = [
        ("-D TEST_INT=13", "-DTEST_INT=13"),
        ("-DTEST_SINGLE_MACRO", "-DTEST_SINGLE_MACRO"),
        ('-DTEST_STR_SPACE="Andrew Smith"', '"-DTEST_STR_SPACE=Andrew Smith"'),
        ("-Iinclude", "-Iinclude"),
        ("-include cpppath-include.h", "cpppath-include.h"),
        ("-Iextra_inc", "-Iextra_inc"),
        ("-Inon-existing-dir", "non-existing-dir"),
        (
            "-include $PROJECT_DIR/lib/component/component-forced-include.h",
            "component-forced-include.h",
        ),
    ]

    tmpdir.join("platformio.ini").write(
        """
[env:native]
platform = native
extra_scripts =
    pre:pre_script.py
    post_script.py
lib_ldf_mode = deep+
build_src_flags = -DI_AM_ONLY_SRC_FLAG
build_flags =
    ; -DCOMMENTED_MACRO
    %s ; inline comment
    """
        % " ".join([f[0] for f in build_flags])
    )

    tmpdir.join("pre_script.py").write(
        """
Import("env")

def post_prog_action(source, target, env):
    print("post_prog_action is called")

env.AddPostAction("$PROGPATH", post_prog_action)
    """
    )
    tmpdir.join("post_script.py").write(
        """
Import("projenv")

projenv.Append(CPPDEFINES="POST_SCRIPT_MACRO")
    """
    )

    tmpdir.mkdir("extra_inc").join("foo.h").write(
        """
#define FOO
    """
    )

    tmpdir.mkdir("src").join("main.cpp").write(
        """
#include "foo.h"

#ifndef FOO
#error "FOO"
#endif

#ifdef I_AM_ONLY_SRC_FLAG
#include <component.h>
#else
#error "I_AM_ONLY_SRC_FLAG"
#endif

#if !defined(TEST_INT) || TEST_INT != 13
#error "TEST_INT"
#endif

#ifndef TEST_STR_SPACE
#error "TEST_STR_SPACE"
#endif

#ifndef I_AM_COMPONENT
#error "I_AM_COMPONENT"
#endif

#ifndef POST_SCRIPT_MACRO
#error "POST_SCRIPT_MACRO"
#endif

#ifndef I_AM_FORCED_COMPONENT_INCLUDE
#error "I_AM_FORCED_COMPONENT_INCLUDE"
#endif

#ifndef I_AM_FORCED_CPPPATH_INCLUDE
#error "I_AM_FORCED_CPPPATH_INCLUDE"
#endif

#ifdef COMMENTED_MACRO
#error "COMMENTED_MACRO"
#endif

int main() {
}
"""
    )

    tmpdir.mkdir("include").join("cpppath-include.h").write(
        """
#define I_AM_FORCED_CPPPATH_INCLUDE
"""
    )
    component_dir = tmpdir.mkdir("lib").mkdir("component")
    component_dir.join("component.h").write(
        """
#define I_AM_COMPONENT

#ifndef I_AM_ONLY_SRC_FLAG
#error "I_AM_ONLY_SRC_FLAG"
#endif

void dummy(void);
    """
    )
    component_dir.join("component.cpp").write(
        """
#ifdef I_AM_ONLY_SRC_FLAG
#error "I_AM_ONLY_SRC_FLAG"
#endif

void dummy(void ) {};
    """
    )
    component_dir.join("component-forced-include.h").write(
        """
#define I_AM_FORCED_COMPONENT_INCLUDE
    """
    )

    result = clirunner.invoke(cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    assert "post_prog_action is called" in result.output
    build_output = result.output[result.output.find("Scanning dependencies...") :]
    for flag in build_flags:
        assert flag[1] in build_output, flag


def test_build_unflags(clirunner, validate_cliresult, tmpdir):
    tmpdir.join("platformio.ini").write(
        """
[env:native]
platform = native
build_unflags =
    -DTMP_MACRO_1=45
    -DTMP_MACRO_3=13
    -DTMP_MACRO_4
    -DNON_EXISTING_MACRO
    -I.
    -lunknownLib
    -Os
build_flags =
    -DTMP_MACRO_3=10
extra_scripts = pre:extra.py
"""
    )

    tmpdir.join("extra.py").write(
        """
Import("env")
env.Append(CPPPATH="%s")
env.Append(CPPDEFINES="TMP_MACRO_1")
env.Append(CPPDEFINES=["TMP_MACRO_2"])
env.Append(CPPDEFINES=[("TMP_MACRO_3", 13)])
env.Append(CPPDEFINES=[("TMP_MACRO_4", 4)])
env.Append(CCFLAGS=["-Os"])
env.Append(LIBS=["unknownLib"])
    """
        % str(tmpdir)
    )

    tmpdir.mkdir("src").join("main.c").write(
        """
#ifndef TMP_MACRO_1
#error "TMP_MACRO_1 should be defined"
#endif

#ifndef TMP_MACRO_2
#error "TMP_MACRO_2 should be defined"
#endif

#if TMP_MACRO_3 != 10
#error "TMP_MACRO_3 should be 10"
#endif

#ifdef TMP_MACRO_4
#error "TMP_MACRO_4 should not be defined"
#endif

int main() {
}
"""
    )

    result = clirunner.invoke(cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    build_output = result.output[result.output.find("Scanning dependencies...") :]
    assert "-DTMP_MACRO1" not in build_output
    assert "-Os" not in build_output
    assert str(tmpdir) not in build_output


def test_debug_default_build_flags(clirunner, validate_cliresult, tmpdir):
    tmpdir.join("platformio.ini").write(
        """
[env:native]
platform = native
build_type = debug
"""
    )

    tmpdir.mkdir("src").join("main.c").write(
        """
int main() {
}
"""
    )

    result = clirunner.invoke(cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    build_output = result.output[result.output.find("Scanning dependencies...") :]
    for line in build_output.split("\n"):
        if line.startswith("gcc"):
            assert all(line.count(flag) == 1 for flag in ("-Og", "-g2", "-ggdb2"))
            assert all(
                line.count("-%s%d" % (flag, level)) == 0
                for flag in ("O", "g", "ggdb")
                for level in (0, 1, 3)
            )
            assert "-Os" not in line


def test_debug_custom_build_flags(clirunner, validate_cliresult, tmpdir):
    custom_debug_build_flags = ("-O3", "-g3", "-ggdb3")

    tmpdir.join("platformio.ini").write(
        """
[env:native]
platform = native
build_type = debug
debug_build_flags = %s
    """
        % " ".join(custom_debug_build_flags)
    )

    tmpdir.mkdir("src").join("main.c").write(
        """
int main() {
}
"""
    )

    result = clirunner.invoke(cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    build_output = result.output[result.output.find("Scanning dependencies...") :]
    for line in build_output.split("\n"):
        if line.startswith("gcc"):
            assert all(line.count(f) == 1 for f in custom_debug_build_flags)
            assert all(
                line.count("-%s%d" % (flag, level)) == 0
                for flag in ("O", "g", "ggdb")
                for level in (0, 1, 2)
            )
            assert all("-O%s" % optimization not in line for optimization in ("g", "s"))


def test_symlinked_libs(clirunner, validate_cliresult, tmp_path: Path):
    external_pkg_dir = tmp_path / "External"
    external_pkg_dir.mkdir()
    (external_pkg_dir / "External.h").write_text(
        """
#define EXTERNAL 1
"""
    )
    (external_pkg_dir / "library.json").write_text(
        """
{
    "name": "External",
    "version": "1.0.0"
}
"""
    )

    project_dir = tmp_path / "project"
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "main.c").write_text(
        """
#include <External.h>
#
#if !defined(EXTERNAL)
#error "EXTERNAL is not defined"
#endif

int main() {
}
"""
    )
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
lib_deps = symlink://../External
    """
    )
    result = clirunner.invoke(cmd_run, ["--project-dir", str(project_dir)])
    validate_cliresult(result)


def test_stringification(clirunner, validate_cliresult, tmp_path: Path):
    project_dir = tmp_path / "project"
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "main.c").write_text(
        """
#include <stdio.h>
int main(void) {
    printf("MACRO_1=<%s>\\n", MACRO_1);
    printf("MACRO_2=<%s>\\n", MACRO_2);
    printf("MACRO_3=<%s>\\n", MACRO_3);
    printf("MACRO_4=<%s>\\n", MACRO_4);
    return(0);
}
"""
    )
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
extra_scripts = script.py
build_flags =
    '-DMACRO_1="Hello World!"'
    '-DMACRO_2="Text is \\\\"Quoted\\\\""'
    """
    )
    (project_dir / "script.py").write_text(
        """
Import("projenv")

projenv.Append(CPPDEFINES=[
    ("MACRO_3", projenv.StringifyMacro('Hello "World"! Isn\\'t true?')),
    ("MACRO_4", projenv.StringifyMacro("Special chars: ',(,),[,],:"))
])
    """
    )
    result = clirunner.invoke(
        cmd_run, ["--project-dir", str(project_dir), "-t", "exec"]
    )
    validate_cliresult(result)
    assert "MACRO_1=<Hello World!>" in result.output
    assert 'MACRO_2=<Text is "Quoted">' in result.output
    assert 'MACRO_3=<Hello "World"! Isn\'t true?>' in result.output
    assert "MACRO_4=<Special chars: ',(,),[,],:>" in result.output


def test_ldf(clirunner, validate_cliresult, tmp_path: Path):
    project_dir = tmp_path / "project"

    # libs
    lib_dir = project_dir / "lib"
    a_lib_dir = lib_dir / "a"
    a_lib_dir.mkdir(parents=True)
    (a_lib_dir / "a.h").write_text(
        """
#include <some_from_b.h>
"""
    )
    # b
    b_lib_dir = lib_dir / "b"
    b_lib_dir.mkdir(parents=True)
    (b_lib_dir / "some_from_b.h").write_text("")
    # c
    c_lib_dir = lib_dir / "c"
    c_lib_dir.mkdir(parents=True)
    (c_lib_dir / "parse_c_by_name.h").write_text(
        """
void some_func();
    """
    )
    (c_lib_dir / "parse_c_by_name.c").write_text(
        """
#include <d.h>
#include <parse_c_by_name.h>

void some_func() {
}
    """
    )
    (c_lib_dir / "some.c").write_text(
        """
#include <d.h>
    """
    )
    # d
    d_lib_dir = lib_dir / "d"
    d_lib_dir.mkdir(parents=True)
    (d_lib_dir / "d.h").write_text("")

    # project
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "main.h").write_text(
        """
#include <a.h>
#include <parse_c_by_name.h>
"""
    )
    (src_dir / "main.c").write_text(
        """
#include <main.h>

int main() {
}
"""
    )
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
    """
    )
    result = clirunner.invoke(cmd_run, ["--project-dir", str(project_dir)])
    validate_cliresult(result)
