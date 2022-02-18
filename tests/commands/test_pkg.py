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

import pytest

from platformio.package.commands.exec import package_exec_cmd


def test_exec(clirunner, validate_cliresult, strip_ansi):
    result = clirunner.invoke(
        package_exec_cmd,
        ["--", "openocd"],
    )
    with pytest.raises(
        AssertionError,
        match=("Could not find a package with 'openocd' executable file"),
    ):
        validate_cliresult(result)

    # with install
    result = clirunner.invoke(
        package_exec_cmd,
        ["-p", "platformio/tool-openocd", "--", "openocd", "--version"],
    )
    validate_cliresult(result)
    output = strip_ansi(result.output)
    assert "Tool Manager: Installing platformio/tool-openocd" in output

    # unrecognized option
    result = clirunner.invoke(
        package_exec_cmd,
        ["--", "openocd", "--test-unrecognized"],
    )
    with pytest.raises(
        AssertionError,
        match=("Using tool-openocd"),
    ):
        validate_cliresult(result)
