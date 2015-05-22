# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
