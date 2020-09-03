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

from platformio.commands.boards import cli as cmd_boards
from platformio.commands.platform import platform_search as cmd_platform_search


def test_board_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ["mbed", "--json-output"])
    validate_cliresult(result)
    boards = json.loads(result.output)
    assert isinstance(boards, list)
    assert any(["mbed" in b["frameworks"] for b in boards])


def test_board_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ["espidf"])
    validate_cliresult(result)
    assert "espressif32" in result.output


def test_board_options(clirunner, validate_cliresult):
    required_opts = set(["fcpu", "frameworks", "id", "mcu", "name", "platform"])

    # fetch available platforms
    result = clirunner.invoke(cmd_platform_search, ["--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert search_result
    platforms = [item["name"] for item in search_result]

    result = clirunner.invoke(cmd_boards, ["mbed", "--json-output"])
    validate_cliresult(result)
    boards = json.loads(result.output)

    for board in boards:
        assert required_opts.issubset(set(board))
        assert board["platform"] in platforms
