# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.


from click.testing import CliRunner

from platformio.commands.settings import cli
from platformio import app

runner = CliRunner()


def validate_output(result):
    assert result.exit_code == 0
    assert not result.exception
    assert "error" not in result.output.lower()


def test_settings_check():
    result = runner.invoke(cli, ["get"])
    validate_output(result)
    assert len(result.output)
    for item in app.DEFAULT_SETTINGS.items():
        assert item[0] in result.output
