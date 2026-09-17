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

from platformio.run.cli import cli as cmd_run


def _make_project_with_tests(tmpdir, extra_ini=""):
    tmpdir.join("platformio.ini").write("""
[env:native]
platform = native
%s
""" % extra_ini)
    tmpdir.mkdir("src").join("calc.c").write("""
int add(int a, int b) { return a + b; }
""")
    tmpdir.mkdir("test").mkdir("test_calc").join("test_add.c").write("""
int add(int a, int b);
int main(void) { return add(1, 2) == 3 ? 0 : 1; }
""")


def _compiledb_files(tmpdir):
    with open(str(tmpdir.join("compile_commands.json")), encoding="utf8") as fp:
        return [entry["file"] for entry in json.load(fp)]


def test_compiledb_includes_test_sources(clirunner, validate_cliresult, tmpdir):
    # Regression test for https://github.com/platformio/platformio-core/issues/4934
    # `pio run -t compiledb -t __test` used to fail with "Nothing to build"
    # for the documented `test/test_*/` layout, leaving test sources (and
    # test-framework headers like unity.h) out of the compilation database.
    _make_project_with_tests(tmpdir)
    result = clirunner.invoke(
        cmd_run,
        ["--project-dir", str(tmpdir), "-t", "compiledb", "-t", "__test"],
    )
    validate_cliresult(result)

    files = _compiledb_files(tmpdir)
    assert any(f.endswith("test_add.c") for f in files), files


def test_compiledb_with_tests_and_src(clirunner, validate_cliresult, tmpdir):
    # With `test_build_src = yes`, both the test suites and the production
    # sources should land in the compilation database.
    _make_project_with_tests(tmpdir, extra_ini="test_build_src = yes")
    result = clirunner.invoke(
        cmd_run,
        ["--project-dir", str(tmpdir), "-t", "compiledb", "-t", "__test"],
    )
    validate_cliresult(result)

    files = _compiledb_files(tmpdir)
    assert any(f.endswith("test_add.c") for f in files), files
    assert any(f.endswith("calc.c") for f in files), files


def test_compiledb_without_test_target_unchanged(clirunner, validate_cliresult, tmpdir):
    # Non-regression: a plain `pio run -t compiledb` must keep its current
    # behavior — production sources only, no test sources.
    _make_project_with_tests(tmpdir)
    result = clirunner.invoke(
        cmd_run, ["--project-dir", str(tmpdir), "-t", "compiledb"]
    )
    validate_cliresult(result)

    files = _compiledb_files(tmpdir)
    assert any(f.endswith("calc.c") for f in files), files
    assert not any(f.endswith("test_add.c") for f in files), files
