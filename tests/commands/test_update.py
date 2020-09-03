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

from platformio.commands.update import cli as cmd_update


def test_update(clirunner, validate_cliresult, isolated_pio_core):
    matches = ("Platform Manager", "Library Manager")
    result = clirunner.invoke(cmd_update, ["--only-check"])
    validate_cliresult(result)
    assert all([m in result.output for m in matches])
    result = clirunner.invoke(cmd_update)
    validate_cliresult(result)
    assert all([m in result.output for m in matches])
