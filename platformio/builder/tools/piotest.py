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

from __future__ import absolute_import

import os

from platformio.unittest.result import TestSuite
from platformio.unittest.runners.factory import TestRunnerFactory


def ConfigureTestTarget(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST", "PIO_UNIT_TESTING"],
        PIOTEST_SRC_FILTER=["+<*.cpp>", "+<*.c>"],
    )

    if "PIOTEST_RUNNING_NAME" in env:
        env.Append(
            PIOTEST_SRC_FILTER=[f"+<$PIOTEST_RUNNING_NAME{os.path.sep}>"],
            CPPPATH=[os.path.join("$PROJECT_TEST_DIR", "$PIOTEST_RUNNING_NAME")],
        )

    env.Append(CPPPATH=["$PROJECT_TEST_DIR"])
    test_runner = TestRunnerFactory.new(
        TestSuite(env["PIOENV"], env.get("PIOTEST_RUNNING_NAME", "*")),
        env.GetProjectConfig(),
    )
    test_runner.configure_build_env(env)


def generate(env):
    env.AddMethod(ConfigureTestTarget)


def exists(_):
    return True
