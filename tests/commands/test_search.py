# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

from platformio.commands.search import cli


def test_search_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["arduino", "--json-output"])
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['name'] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["arduino"])
    validate_cliresult(result)
    assert "teensy" in result.output
