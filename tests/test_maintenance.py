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

import json
import os
import re
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


def test_check_lib_updates(clirunner, isolated_pio_core, validate_cliresult):
    # install obsolete library
    result = clirunner.invoke(cli_pio, ["lib", "-g", "install", "ArduinoJson@<6.13"])
    validate_cliresult(result)

    # reset check time
    interval = int(app.get_setting("check_libraries_interval")) * 3600 * 24
    last_check = {"libraries_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    result = clirunner.invoke(cli_pio, ["lib", "-g", "list"])
    validate_cliresult(result)
    assert "There are the new updates for libraries (ArduinoJson)" in result.output


def test_check_and_update_libraries(clirunner, isolated_pio_core, validate_cliresult):
    # enable library auto-updates
    result = clirunner.invoke(
        cli_pio, ["settings", "set", "auto_update_libraries", "Yes"]
    )

    # reset check time
    interval = int(app.get_setting("check_libraries_interval")) * 3600 * 24
    last_check = {"libraries_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    # fetch installed version
    result = clirunner.invoke(cli_pio, ["lib", "-g", "list", "--json-output"])
    validate_cliresult(result)
    prev_data = json.loads(result.output)
    assert len(prev_data) == 1

    # initiate auto-updating
    result = clirunner.invoke(cli_pio, ["lib", "-g", "show", "ArduinoJson"])
    validate_cliresult(result)
    assert "There are the new updates for libraries (ArduinoJson)" in result.output
    assert "Please wait while updating libraries" in result.output
    assert re.search(
        r"Updating bblanchon/ArduinoJson\s+6\.12\.0\s+\[Outdated [\d\.]+\]",
        result.output,
    )

    # check updated version
    result = clirunner.invoke(cli_pio, ["lib", "-g", "list", "--json-output"])
    validate_cliresult(result)
    assert prev_data[0]["version"] != json.loads(result.output)[0]["version"]


def test_check_platform_updates(clirunner, isolated_pio_core, validate_cliresult):
    # install obsolete platform
    result = clirunner.invoke(cli_pio, ["platform", "install", "native"])
    validate_cliresult(result)
    os.remove(str(isolated_pio_core.join("platforms", "native", ".piopm")))
    manifest_path = isolated_pio_core.join("platforms", "native", "platform.json")
    manifest = json.loads(manifest_path.read())
    manifest["version"] = "0.0.0"
    manifest_path.write(json.dumps(manifest))

    # reset check time
    interval = int(app.get_setting("check_platforms_interval")) * 3600 * 24
    last_check = {"platforms_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    result = clirunner.invoke(cli_pio, ["platform", "list"])
    validate_cliresult(result)
    assert "There are the new updates for platforms (native)" in result.output


def test_check_and_update_platforms(clirunner, isolated_pio_core, validate_cliresult):
    # enable library auto-updates
    result = clirunner.invoke(
        cli_pio, ["settings", "set", "auto_update_platforms", "Yes"]
    )

    # reset check time
    interval = int(app.get_setting("check_platforms_interval")) * 3600 * 24
    last_check = {"platforms_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    # fetch installed version
    result = clirunner.invoke(cli_pio, ["platform", "list", "--json-output"])
    validate_cliresult(result)
    prev_data = json.loads(result.output)
    assert len(prev_data) == 1

    # initiate auto-updating
    result = clirunner.invoke(cli_pio, ["platform", "show", "native"])
    validate_cliresult(result)
    assert "There are the new updates for platforms (native)" in result.output
    assert "Please wait while updating platforms" in result.output
    assert re.search(r"Updating native\s+0.0.0\s+\[Outdated [\d\.]+\]", result.output)

    # check updated version
    result = clirunner.invoke(cli_pio, ["platform", "list", "--json-output"])
    validate_cliresult(result)
    assert prev_data[0]["version"] != json.loads(result.output)[0]["version"]
