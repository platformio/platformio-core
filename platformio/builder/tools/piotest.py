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

import os

from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error

from platformio.builder.tools import piobuild
from platformio.test.result import TestSuite
from platformio.test.runners.factory import TestRunnerFactory


def ConfigureTestTarget(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST"],  # deprecated, use PIO_UNIT_TESTING
        PIOTEST_SRC_FILTER=[f"+<*.{ext}>" for ext in piobuild.SRC_BUILD_EXT],
    )
    env.Prepend(CPPPATH=["$PROJECT_TEST_DIR"])

    if "PIOTEST_RUNNING_NAME" not in env and "compiledb" in COMMAND_LINE_TARGETS:
        # A compilation database is being generated without a specific test
        # suite selected (`pio run -t compiledb -t __test`, issue #4934).
        # The default filter above only matches sources directly in the test
        # dir, so nested `test_*/` suites — the documented layout — would
        # produce "Nothing to build". Include every test suite recursively:
        # unlike a real test build, compiledb never links, so the multiple
        # `main()` definitions across suites are not a problem.
        env.Append(PIOTEST_SRC_FILTER=[f"+<test_*{os.path.sep}>"])
        test_dir = env.subst("$PROJECT_TEST_DIR")
        if os.path.isdir(test_dir):
            for item in sorted(os.listdir(test_dir)):
                if item.startswith("test_") and os.path.isdir(
                    os.path.join(test_dir, item)
                ):
                    env.Prepend(CPPPATH=[os.path.join("$PROJECT_TEST_DIR", item)])

    if "PIOTEST_RUNNING_NAME" in env:
        test_name = env["PIOTEST_RUNNING_NAME"]
        while True:
            test_name = os.path.dirname(test_name)  # parent dir
            # skip nested tests (user's side issue?)
            if not test_name or os.path.basename(test_name).startswith("test_"):
                break
            env.Prepend(
                PIOTEST_SRC_FILTER=[
                    f"+<{test_name}{os.path.sep}*.{ext}>"
                    for ext in piobuild.SRC_BUILD_EXT
                ],
                CPPPATH=[os.path.join("$PROJECT_TEST_DIR", test_name)],
            )

        env.Prepend(
            PIOTEST_SRC_FILTER=[f"+<$PIOTEST_RUNNING_NAME{os.path.sep}>"],
            CPPPATH=[os.path.join("$PROJECT_TEST_DIR", "$PIOTEST_RUNNING_NAME")],
        )

    test_runner = TestRunnerFactory.new(
        TestSuite(env["PIOENV"], env.get("PIOTEST_RUNNING_NAME", "*")),
        env.GetProjectConfig(),
    )
    test_runner.configure_build_env(env)


def generate(env):
    env.AddMethod(ConfigureTestTarget)


def exists(_):
    return True
