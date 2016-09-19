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

from os.path import join

import pytest

from platformio import util


def test_local_env():
    result = util.exec_command(["platformio", "test", "-d",
                                join("examples", "unit-testing", "calculator"),
                                "-e", "local"])
    if result['returncode'] != 1:
        pytest.fail(result)
    assert all(
        [s in result['out'] for s in ("[PASSED]", "[IGNORED]", "[FAILED]")])
