# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json


from click.testing import CliRunner

from platformio.commands.list import cli

runner = CliRunner()


def validate_output(result):
    assert result.exit_code == 0
    assert not result.exception
    assert "error" not in result.output.lower()


def test_list_json_output():
    result = runner.invoke(cli, ["--json-output"])
    validate_output(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert len(list_result)
    platforms = [item['name'] for item in list_result]
    assert "titiva" in platforms


def test_list_raw_output():
    result = runner.invoke(cli)
    validate_output(result)
    assert "teensy" in result.output
