# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json


from click.testing import CliRunner

from platformio.commands.search import cli

runner = CliRunner()


def validate_output(result):
    assert result.exit_code == 0
    assert not result.exception
    assert "error" not in result.output.lower()


def test_search_json_output():
    result = runner.invoke(cli, ["arduino", "--json-output"])
    validate_output(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['name'] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output():
    result = runner.invoke(cli, ["arduino"])
    validate_output(result)
    assert "digistump" in result.output
