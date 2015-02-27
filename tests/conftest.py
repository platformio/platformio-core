# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click.testing import CliRunner

import pytest
from platformio import app


@pytest.fixture(scope="session")
def platformio_setup(request):
    prev_settings = dict(
        enable_telemetry=None,
        enable_prompts=None
    )
    for key, value in prev_settings.iteritems():
        prev_settings[key] = app.get_setting(key)
        # disable temporary
        if prev_settings[key]:
            app.set_setting(key, False)

    def platformio_teardown():
        # restore settings
        for key, value in prev_settings.iteritems():
            app.set_setting(key, value)

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
