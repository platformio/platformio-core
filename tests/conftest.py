# Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
