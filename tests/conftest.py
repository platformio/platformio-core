# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import environ

from click.testing import CliRunner

import pytest


@pytest.fixture(scope="session")
def platformio_setup(request):
    pioenvvars = ("ENABLE_PROMPTS", "ENABLE_TELEMETRY")
    for v in pioenvvars:
        environ["PLATFORMIO_SETTING_%s" % v] = "No"

    def platformio_teardown():
        for v in pioenvvars:
            _name = "PLATFORMIO_SETTING_%s" % v
            if _name in environ:
                del environ[_name]

    request.addfinalizer(platformio_teardown)


@pytest.fixture(scope="session")
def clirunner():
    return CliRunner()


@pytest.fixture(scope="session")
def validate_cliresult():
    def decorator(result):
        assert result.exit_code == 0
        assert not result.exception
        assert "error" not in result.output.lower()
    return decorator
