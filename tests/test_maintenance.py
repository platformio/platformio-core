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

import json
import re
from time import time

from platformio import app, maintenance
from platformio.__main__ import cli as cli_pio
from platformio.commands import upgrade as cmd_upgrade
from platformio.managers.platform import PlatformManager


def test_after_upgrade_2_to_3(clirunner, validate_cliresult,
                              isolated_pio_home):
    app.set_state_item("last_version", "2.11.2")
    app.set_state_item("installed_platforms", ["native"])

    # generate PlatformIO 2.0 boards
    boards = isolated_pio_home.mkdir("boards")
    board_ids = set()
    for prefix in ("foo", "bar"):
        data = {}
        for i in range(3):
            board_id = "board_%s_%d" % (prefix, i)
            board_ids.add(board_id)
            data[board_id] = {
                "name": "Board %s #%d" % (prefix, i),
                "url": "",
                "vendor": ""
            }
        boards.join(prefix + ".json").write(json.dumps(data))

    result = clirunner.invoke(cli_pio, ["settings", "get"])
    validate_cliresult(result)
    assert "upgraded to " in result.output

    # check PlatformIO 3.0 boards
    assert board_ids == set([p.basename[:-5] for p in boards.listdir()])

    result = clirunner.invoke(cli_pio,
                              ["boards", "--installed", "--json-output"])
    validate_cliresult(result)
    assert board_ids == set([b['id'] for b in json.loads(result.output)])


def test_after_upgrade_silence(clirunner, validate_cliresult):
    app.set_state_item("last_version", "2.11.2")
    result = clirunner.invoke(cli_pio, ["boards", "--json-output"])
    validate_cliresult(result)
    boards = json.loads(result.output)
    assert any([b['id'] == "uno" for b in boards])


def test_check_pio_upgrade(clirunner, validate_cliresult):

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


def test_check_lib_updates(clirunner, validate_cliresult):
    # install obsolete library
    result = clirunner.invoke(cli_pio,
                              ["lib", "-g", "install", "ArduinoJson@<5.7"])
    validate_cliresult(result)

    # reset check time
    interval = int(app.get_setting("check_libraries_interval")) * 3600 * 24
    last_check = {"libraries_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    result = clirunner.invoke(cli_pio, ["lib", "-g", "list"])
    validate_cliresult(result)
    assert ("There are the new updates for libraries (ArduinoJson)" in
            result.output)


def test_check_and_update_libraries(clirunner, validate_cliresult):
    # enable library auto-updates
    result = clirunner.invoke(
        cli_pio, ["settings", "set", "auto_update_libraries", "Yes"])

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
    assert ("There are the new updates for libraries (ArduinoJson)" in
            result.output)
    assert "Please wait while updating libraries" in result.output
    assert re.search(r"Updating ArduinoJson\s+@ 5.6.7\s+\[[\d\.]+\]",
                     result.output)

    # check updated version
    result = clirunner.invoke(cli_pio, ["lib", "-g", "list", "--json-output"])
    validate_cliresult(result)
    assert prev_data[0]['version'] != json.loads(result.output)[0]['version']


def test_check_platform_updates(clirunner, validate_cliresult,
                                isolated_pio_home):
    # install obsolete platform
    result = clirunner.invoke(cli_pio, ["platform", "install", "native"])
    validate_cliresult(result)
    manifest_path = isolated_pio_home.join("platforms", "native",
                                           "platform.json")
    manifest = json.loads(manifest_path.read())
    manifest['version'] = "0.0.0"
    manifest_path.write(json.dumps(manifest))
    # reset cached manifests
    PlatformManager().cache_reset()

    # reset check time
    interval = int(app.get_setting("check_platforms_interval")) * 3600 * 24
    last_check = {"platforms_update": time() - interval - 1}
    app.set_state_item("last_check", last_check)

    result = clirunner.invoke(cli_pio, ["platform", "list"])
    validate_cliresult(result)
    assert "There are the new updates for platforms (native)" in result.output


def test_check_and_update_platforms(clirunner, validate_cliresult):
    # enable library auto-updates
    result = clirunner.invoke(
        cli_pio, ["settings", "set", "auto_update_platforms", "Yes"])

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
    assert re.search(r"Updating native\s+@ 0.0.0\s+\[[\d\.]+\]", result.output)

    # check updated version
    result = clirunner.invoke(cli_pio, ["platform", "list", "--json-output"])
    validate_cliresult(result)
    assert prev_data[0]['version'] != json.loads(result.output)[0]['version']
