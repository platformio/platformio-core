# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import os

import pytest
import requests
from click.testing import CliRunner

requests.packages.urllib3.disable_warnings()


@pytest.fixture(scope="module")
def clirunner():
    return CliRunner()


@pytest.fixture(scope="session")
def validate_cliresult():

    def decorator(result):
        assert result.exit_code == 0
        assert not result.exception

    return decorator


@pytest.fixture(scope="module")
def isolated_pio_home(request, tmpdir_factory):
    home_dir = tmpdir_factory.mktemp(".platformio")
    os.environ['PLATFORMIO_HOME_DIR'] = str(home_dir)

    def fin():
        del os.environ['PLATFORMIO_HOME_DIR']

    request.addfinalizer(fin)
    return home_dir
