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

import json
import re
from os.path import basename

from platformio import util
from platformio.commands.init import cli as cmd_init
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
        "-g", "install", "58", "OneWire",
        "http://dl.platformio.org/libraries/archives/3/5174.tar.gz",
        "ArduinoJson@5.6.7", "ArduinoJson@~5.7.0"
    ])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "DHT22_ID58", "ArduinoJson_ID64", "ArduinoJson_ID64@5.6.7",
        "OneWire_ID1", "ESPAsyncTCP_ID305"
    ]
    assert set(items1) == set(items2)


def test_global_install_archive(clirunner, validate_cliresult,
                                isolated_pio_home):
    result = clirunner.invoke(cmd_lib, [
        "-g", "install", "https://github.com/adafruit/Adafruit-ST7735-Library/"
        "archive/master.zip",
        "http://www.airspayce.com/mikem/arduino/RadioHead/RadioHead-1.62.zip"
    ])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = ["Adafruit ST7735 Library", "RadioHead"]
    assert set(items1) >= set(items2)


def test_global_install_repository(clirunner, validate_cliresult,
                                   isolated_pio_home):
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/gioblu/PJON.git#3.0",
            "https://gitlab.com/ivankravets/rs485-nodeproto.git",
            # "https://developer.mbed.org/users/simon/code/TextLCD/",
            "knolleary/pubsubclient"
        ])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = ["PJON", "ESPAsyncTCP", "PubSubClient"]
    assert set(items2) & set(items1)


def test_global_lib_list(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cmd_lib, ["-g", "list"])
    validate_cliresult(result)
    assert all([n in result.output for n in ("OneWire", "DHT22", "64")])

    result = clirunner.invoke(cmd_lib, ["-g", "list", "--json-output"])
    assert all([
        n in result.output
        for n in ("PJON", "git+https://github.com/knolleary/pubsubclient")
    ])
    items1 = [i['name'] for i in json.loads(result.output)]
    items2 = [
        "OneWire", "DHT22", "PJON", "ESPAsyncTCP", "ArduinoJson",
        "pubsubclient", "rs485-nodeproto", "Adafruit ST7735 Library",
        "RadioHead"
    ]
    assert set(items1) == set(items2)


def test_global_lib_update_check(clirunner, validate_cliresult,
                                 isolated_pio_home):
    result = clirunner.invoke(
        cmd_lib, ["-g", "update", "--only-check", "--json-output"])
    validate_cliresult(result)
    output = json.loads(result.output)
    assert set(["ArduinoJson", "RadioHead"]) == set(
        [l['name'] for l in output])


def test_global_lib_update(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cmd_lib, ["-g", "update"])
    validate_cliresult(result)
    assert "[Up-to-date]" in result.output
    assert "Uninstalling ArduinoJson @ 5.7.3" in result.output


def test_global_lib_uninstall(clirunner, validate_cliresult,
                              isolated_pio_home):
    result = clirunner.invoke(cmd_lib, [
        "-g", "uninstall", "1", "ArduinoJson@!=5.6.7", "TextLCD",
        "Adafruit ST7735 Library"
    ])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = [
        "DHT22_ID58", "ArduinoJson_ID64@5.6.7", "ESPAsyncTCP_ID305",
        "pubsubclient", "PJON", "rs485-nodeproto", "RadioHead_ID124"
    ]
    assert set(items1) == set(items2)


def test_lib_show(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cmd_lib, ["show", "64"])
    validate_cliresult(result)
    assert all(
        [s in result.output for s in ("ArduinoJson", "Arduino", "Atmel AVR")])
    result = clirunner.invoke(cmd_lib, ["show", "OneWire"])
    validate_cliresult(result)
    assert "OneWire" in result.output


def test_project_lib_complex(clirunner, validate_cliresult, tmpdir):
    with tmpdir.as_cwd():
        # init
        result = clirunner.invoke(cmd_init)
        validate_cliresult(result)

        # isntall
        result = clirunner.invoke(cmd_lib, ["install", "54", "ArduinoJson"])
        validate_cliresult(result)
        items1 = [
            d.basename
            for d in tmpdir.join(basename(util.get_projectlibdeps_dir()))
            .listdir()
        ]
        items2 = ["DallasTemperature_ID54", "OneWire_ID1", "ArduinoJson_ID64"]
        assert set(items1) == set(items2)

        # list
        result = clirunner.invoke(cmd_lib, ["list", "--json-output"])
        validate_cliresult(result)
        items1 = [i['name'] for i in json.loads(result.output)]
        items2 = ["DallasTemperature", "OneWire", "ArduinoJson"]
        assert set(items1) == set(items2)

        # update
        result = clirunner.invoke(cmd_lib, ["update"])
        validate_cliresult(result)
        assert "[Up-to-date]" in result.output
