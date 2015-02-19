# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import pytest

from platformio import app


@pytest.fixture(scope="module")
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
