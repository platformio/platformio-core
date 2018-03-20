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

from platformio.commands.run import cli as cmd_run


def test_build_flags(clirunner, validate_cliresult, tmpdir):
    build_flags = [("-D TEST_INT=13", "-DTEST_INT=13"),
                   ("-DTEST_SINGLE_MACRO", "-DTEST_SINGLE_MACRO"),
                   ('-DTEST_STR_SPACE="Andrew Smith"',
                    '"-DTEST_STR_SPACE=Andrew Smith"')]

    tmpdir.join("platformio.ini").write("""
[env:native]
platform = native
extra_scripts = extra.py
build_flags = %s
    """ % " ".join([f[0] for f in build_flags]))

    tmpdir.join("extra.py").write("""
Import("env")
env.Append(CPPDEFINES="POST_SCRIPT_MACRO")
    """)

    tmpdir.mkdir("src").join("main.cpp").write("""
#if !defined(TEST_INT) || TEST_INT != 13
#error "TEST_INT"
#endif

#ifndef TEST_STR_SPACE
#error "TEST_STR_SPACE"
#endif

#ifndef POST_SCRIPT_MACRO
#error "POST_SCRIPT_MACRO"
#endif

int main() {
}
""")

    result = clirunner.invoke(
        cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    build_output = result.output[result.output.find(
        "Scanning dependencies..."):]
    for flag in build_flags:
        assert flag[1] in build_output, flag


def test_build_unflags(clirunner, validate_cliresult, tmpdir):
    tmpdir.join("platformio.ini").write("""
[env:native]
platform = native
build_unflags = -DTMP_MACRO1=45 -I. -DNON_EXISTING_MACRO
extra_scripts = pre:extra.py
""")

    tmpdir.join("extra.py").write("""
Import("env")
env.Append(CPPPATH="%s")
env.Append(CPPDEFINES="TMP_MACRO1")
env.Append(CPPDEFINES=["TMP_MACRO2"])
env.Append(CPPDEFINES=("TMP_MACRO3", 13))
    """ % str(tmpdir))

    tmpdir.mkdir("src").join("main.c").write("""
#ifdef TMP_MACRO1
#error "TMP_MACRO1 should be removed"
#endif

int main() {
}
""")

    result = clirunner.invoke(
        cmd_run, ["--project-dir", str(tmpdir), "--verbose"])
    validate_cliresult(result)
    build_output = result.output[result.output.find(
        "Scanning dependencies..."):]
    assert "-DTMP_MACRO1" not in build_output
    assert str(tmpdir) not in build_output
