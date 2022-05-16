# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

# pylint: disable=unused-argument

from time import time

from platformio import app, maintenance
from platformio.__main__ import cli as cli_pio
from platformio.commands import upgrade as cmd_upgrade


def test_check_pio_upgrade(clirunner, isolated_pio_core, validate_cliresult):
    def _patch_pio_version(version):
        maintenance.__version__ = version
        cmd_upgrade.VERSION = version.split(".", 3)

    interval = int(app.get_setting("check_platformio_interval")) * 3600 * 24
    last_check = {"platformio_upgrade": time() - interval - 1}
    origin_version = maintenance.__version__

    # check development version
    _patch_pio_version("3.0.0-a1")
    app.set_state_item("last_check", last_check)
    result = clirunner.invoke(cli_pio, ["platform", "list"])
    validate_cliresult(result)
    assert "There is a new version" in result.output
    assert "Please upgrade" in result.output

    # check stable version
    _patch_pio_version("2.11.0")
    app.set_state_item("last_check", last_check)
    result = clirunner.invoke(cli_pio, ["platform", "list"])
    validate_cliresult(result)
    assert "There is a new version" in result.output
    assert "Please upgrade" in result.output

    # restore original version
    _patch_pio_version(origin_version)
