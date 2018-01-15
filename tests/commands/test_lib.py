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

from platformio import exception
from platformio.commands.lib import cli as cmd_lib


def test_search(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["search", "DHT22"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) > 2

    result = clirunner.invoke(cmd_lib,
                              ["search", "DHT22", "--platform=timsp430"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) > 1


def test_global_install_registry(clirunner, validate_cliresult,
                                 isolated_pio_home):
    result = clirunner.invoke(cmd_lib, [
        "-g", "install", "64", "ArduinoJson@~5.10.0", "547@2.2.4",
        "AsyncMqttClient@<=0.8.2", "999@77d4eb3f8a"
    ])
    validate_cliresult(result)

    # install unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "install", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, exception.LibNotFound)

    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "ArduinoJson_ID64", "ArduinoJson_ID64@5.10.1", "NeoPixelBus_ID547",
        "AsyncMqttClient_ID346", "ESPAsyncTCP_ID305", "AsyncTCP_ID1826",
        "RFcontrol_ID999"
    ]
    assert set(items1) == set(items2)


def test_global_install_archive(clirunner, validate_cliresult,
                                isolated_pio_home):
    result = clirunner.invoke(cmd_lib, [
        "-g", "install",
        "http://www.airspayce.com/mikem/arduino/RadioHead/RadioHead-1.62.zip",
        "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip",
        "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip@5.8.2",
        "http://dl.platformio.org/libraries/archives/0/9540.tar.gz",
        "https://github.com/adafruit/Adafruit-ST7735-Library/archive/master.zip"
    ])
    validate_cliresult(result)

    # incorrect requirements
    result = clirunner.invoke(cmd_lib, [
        "-g", "install",
        "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip@1.2.3"
    ])
    assert result.exit_code != 0

    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "RadioHead-1.62", "ArduinoJson", "DallasTemperature_ID54",
        "OneWire_ID1", "Adafruit ST7735 Library"
    ]
    assert set(items1) >= set(items2)


def test_global_install_repository(clirunner, validate_cliresult,
                                   isolated_pio_home):
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/gioblu/PJON.git#3.0",
            "https://github.com/gioblu/PJON.git#6.2",
            "https://github.com/bblanchon/ArduinoJson.git",
            "https://gitlab.com/ivankravets/rs485-nodeproto.git",
            "https://github.com/platformio/platformio-libmirror.git",
            # "https://developer.mbed.org/users/simon/code/TextLCD/",
            "knolleary/pubsubclient#bef58148582f956dfa772687db80c44e2279a163"
        ])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "PJON", "PJON@src-79de467ebe19de18287becff0a1fb42d",
        "ArduinoJson@src-69ebddd821f771debe7ee734d3c7fa81", "rs485-nodeproto",
        "platformio-libmirror", "PubSubClient"
    ]
    assert set(items1) >= set(items2)


def test_install_duplicates(clirunner, validate_cliresult, without_internet):
    # registry
    result = clirunner.invoke(cmd_lib, [
        "-g", "install",
        "http://dl.platformio.org/libraries/archives/0/9540.tar.gz"
    ])
    validate_cliresult(result)
    assert "is already installed" in result.output

    # by ID
    result = clirunner.invoke(cmd_lib, ["-g", "install", "999"])
    validate_cliresult(result)
    assert "is already installed" in result.output

    # archive
    result = clirunner.invoke(cmd_lib, [
        "-g", "install",
        "http://www.airspayce.com/mikem/arduino/RadioHead/RadioHead-1.62.zip"
    ])
    validate_cliresult(result)
    assert "is already installed" in result.output

    # repository
    result = clirunner.invoke(cmd_lib, [
        "-g", "install",
        "https://github.com/platformio/platformio-libmirror.git"
    ])
    validate_cliresult(result)
    assert "is already installed" in result.output


def test_global_lib_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["-g", "list"])
    validate_cliresult(result)
    assert all([
        n in result.output for n in
        ("Source: https://github.com/adafruit/Adafruit-ST7735-Library/archive/master.zip",
         "Version: 5.10.1",
         "Source: git+https://github.com/gioblu/PJON.git#3.0",
         "Version: 1fb26fd", "RadioHead-1.62")
    ])

    result = clirunner.invoke(cmd_lib, ["-g", "list", "--json-output"])
    assert all([
        n in result.output for n in
        ("__pkg_dir",
         '"__src_url": "git+https://gitlab.com/ivankravets/rs485-nodeproto.git"',
         '"version": "5.10.1"')
    ])
    items1 = [i['name'] for i in json.loads(result.output)]
    items2 = [
        "Adafruit ST7735 Library", "ArduinoJson", "ArduinoJson", "ArduinoJson",
        "ArduinoJson", "AsyncMqttClient", "AsyncTCP", "DallasTemperature",
        "ESPAsyncTCP", "NeoPixelBus", "OneWire", "PJON", "PJON",
        "PubSubClient", "RFcontrol", "RadioHead-1.62", "platformio-libmirror",
        "rs485-nodeproto"
    ]
    assert sorted(items1) == sorted(items2)

    versions1 = [
        "{name}@{version}".format(**item)
        for item in json.loads(result.output)
    ]
    versions2 = [
        'ArduinoJson@5.8.2', 'ArduinoJson@5.10.1', 'AsyncMqttClient@0.8.2',
        'AsyncTCP@1.0.1', 'ESPAsyncTCP@1.1.3', 'NeoPixelBus@2.2.4',
        'PJON@07fe9aa', 'PJON@1fb26fd', 'PubSubClient@bef5814',
        'RFcontrol@77d4eb3f8a', 'RadioHead-1.62@0.0.0'
    ]
    assert set(versions1) >= set(versions2)


def test_global_lib_update_check(clirunner, validate_cliresult):
    result = clirunner.invoke(
        cmd_lib, ["-g", "update", "--only-check", "--json-output"])
    validate_cliresult(result)
    output = json.loads(result.output)
    assert set(["RFcontrol",
                "NeoPixelBus"]) == set([l['name'] for l in output])


def test_global_lib_update(clirunner, validate_cliresult):
    # update library using package directory
    result = clirunner.invoke(
        cmd_lib,
        ["-g", "update", "NeoPixelBus", "--only-check", "--json-output"])
    validate_cliresult(result)
    oudated = json.loads(result.output)
    assert len(oudated) == 1
    assert "__pkg_dir" in oudated[0]
    result = clirunner.invoke(cmd_lib,
                              ["-g", "update", oudated[0]['__pkg_dir']])
    validate_cliresult(result)
    assert "Uninstalling NeoPixelBus @ 2.2.4" in result.output

    # update rest libraries
    result = clirunner.invoke(cmd_lib, ["-g", "update"])
    validate_cliresult(result)
    assert result.output.count("[Fixed]") == 6
    assert result.output.count("[Up-to-date]") == 11
    assert "Uninstalling RFcontrol @ 77d4eb3f8a" in result.output

    # update unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "update", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, exception.UnknownPackage)


def test_global_lib_uninstall(clirunner, validate_cliresult,
                              isolated_pio_home):
    # uninstall using package directory
    result = clirunner.invoke(cmd_lib, ["-g", "list", "--json-output"])
    validate_cliresult(result)
    items = json.loads(result.output)
    result = clirunner.invoke(cmd_lib,
                              ["-g", "uninstall", items[0]['__pkg_dir']])
    validate_cliresult(result)
    assert "Uninstalling Adafruit ST7735 Library" in result.output

    # uninstall the rest libraries
    result = clirunner.invoke(cmd_lib, [
        "-g", "uninstall", "1", "https://github.com/bblanchon/ArduinoJson.git",
        "ArduinoJson@!=5.6.7", "RFcontrol"
    ])
    validate_cliresult(result)

    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "RadioHead-1.62", "rs485-nodeproto", "platformio-libmirror",
        "PubSubClient", "ArduinoJson@src-69ebddd821f771debe7ee734d3c7fa81",
        "ESPAsyncTCP_ID305", "DallasTemperature_ID54", "NeoPixelBus_ID547",
        "PJON", "AsyncMqttClient_ID346", "ArduinoJson_ID64",
        "PJON@src-79de467ebe19de18287becff0a1fb42d", "AsyncTCP_ID1826"
    ]
    assert set(items1) == set(items2)

    # uninstall unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "uninstall", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, exception.UnknownPackage)


def test_lib_show(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["show", "64"])
    validate_cliresult(result)
    assert all(
        [s in result.output for s in ("ArduinoJson", "Arduino", "Atmel AVR")])
    result = clirunner.invoke(cmd_lib, ["show", "OneWire"])
    validate_cliresult(result)
    assert "OneWire" in result.output


def test_lib_builtin(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["builtin"])
    validate_cliresult(result)
    result = clirunner.invoke(cmd_lib, ["builtin", "--json-output"])
    validate_cliresult(result)


def test_lib_stats(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["stats"])
    validate_cliresult(result)
    assert all([
        s in result.output
        for s in ("UPDATED", "POPULAR", "http://platformio.org/lib/show")
    ])

    result = clirunner.invoke(cmd_lib, ["stats", "--json-output"])
    validate_cliresult(result)
    assert set([
        "dlweek", "added", "updated", "topkeywords", "dlmonth", "dlday",
        "lastkeywords"
    ]) == set(json.loads(result.output).keys())
