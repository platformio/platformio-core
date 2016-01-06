# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

from platformio import util
from platformio.commands.boards import cli as cmd_boards
from platformio.commands.platforms import \
    platforms_search as cmd_platforms_search


def test_board_json_output(platformio_setup, clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ["cortex", "--json-output"])
    validate_cliresult(result)
    boards = json.loads(result.output)
    assert isinstance(boards, dict)
    assert "teensy30" in boards


def test_board_raw_output(platformio_setup, clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ["energia"])
    validate_cliresult(result)
    assert "titiva" in result.output


def test_board_options(platformio_setup, clirunner, validate_cliresult):
    required_opts = set(
        ["build", "platform", "upload", "name"])

    # fetch available platforms
    result = clirunner.invoke(cmd_platforms_search, ["--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['type'] for item in search_result]

    for _, opts in util.get_boards().iteritems():
        assert required_opts.issubset(set(opts))
        assert opts['platform'] in platforms
