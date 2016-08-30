# Copyright 2014-present PlatformIO <contact@platformio.org>
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

from os import listdir
from os.path import dirname, isdir, join, normpath

import pytest

from platformio import util


def pytest_generate_tests(metafunc):
    if "piotest_dir" not in metafunc.fixturenames:
        return
    test_dir = normpath(join(dirname(__file__), "ino2cpp"))
    test_dirs = []
    for name in listdir(test_dir):
        if isdir(join(test_dir, name)):
            test_dirs.append(join(test_dir, name))
    test_dirs.sort()
    metafunc.parametrize("piotest_dir", test_dirs)


@pytest.mark.examples
def test_ci(platformio_setup, piotest_dir):
    result = util.exec_command(
        ["platformio", "--force", "ci", piotest_dir, "-b", "uno"]
    )
    if result['returncode'] != 0:
        pytest.fail(result)
