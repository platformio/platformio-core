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

from platformio.commands.platforms import \
    platforms_list as cmd_platforms_list
from platformio.commands.platforms import \
    platforms_search as cmd_platforms_search


def test_list_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_platforms_list, ["--json-output"])
    validate_cliresult(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert len(list_result)
    platforms = [item['name'] for item in list_result]
    assert "titiva" in platforms


def test_list_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_platforms_list)
    validate_cliresult(result)
    assert "teensy" in result.output


def test_search_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_platforms_search,
                              ["arduino", "--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['type'] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_platforms_search, ["arduino"])
    validate_cliresult(result)
    assert "teensy" in result.output
