# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

from platformio.commands.list import cli


def test_list_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["--json-output"])
    validate_cliresult(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert len(list_result)
    platforms = [item['name'] for item in list_result]
    assert "titiva" in platforms


def test_list_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli)
    validate_cliresult(result)
    assert "teensy" in result.output
