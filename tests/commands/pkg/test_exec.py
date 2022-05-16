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

# pylint: disable=unused-argument

import pytest

from platformio.package.commands.exec import package_exec_cmd
from platformio.util import strip_ansi_codes


def test_pkg_not_installed(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        package_exec_cmd,
        ["--", "openocd"],
    )
    with pytest.raises(
        AssertionError,
        match=("Could not find a package with 'openocd' executable file"),
    ):
        validate_cliresult(result)


def test_pkg_specified(clirunner, validate_cliresult, isolated_pio_core):
    # with install
    result = clirunner.invoke(
        package_exec_cmd,
        ["-p", "platformio/tool-openocd", "--", "openocd", "--version"],
        obj=dict(force_click_stream=True),
    )
    validate_cliresult(result)
    output = strip_ansi_codes(result.output)
    assert "Tool Manager: Installing platformio/tool-openocd" in output
    assert "Open On-Chip Debugger" in output


def test_unrecognized_options(clirunner, validate_cliresult, isolated_pio_core):
    # unrecognized option
    result = clirunner.invoke(
        package_exec_cmd,
        ["--", "openocd", "--test-unrecognized"],
        obj=dict(force_click_stream=True),
    )
    with pytest.raises(
        AssertionError,
        match=(r"openocd: (unrecognized|unknown) option"),
    ):
        validate_cliresult(result)
