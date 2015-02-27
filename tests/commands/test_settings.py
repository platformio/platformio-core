# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.commands.settings import cli
from platformio import app


def test_settings_check(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["get"])
    validate_cliresult(result)
    assert len(result.output)
    for item in app.DEFAULT_SETTINGS.items():
        assert item[0] in result.output
