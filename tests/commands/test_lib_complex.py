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

# pylint: disable=line-too-long

import json
import re

from platformio.cli import PlatformioCLI
from platformio.commands.lib import cli as cmd_lib
from platformio.package.exception import UnknownPackageError
from platformio.util import strip_ansi_codes

PlatformioCLI.leftover_args = ["--json-output"]  # hook for click
ARDUINO_JSON_VERSION = "6.21.5"


def test_search(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["search", "DHT22"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\spackages", result.output)
    assert int(match.group(1)) > 2

    result = clirunner.invoke(cmd_lib, ["search", "DHT22", "--platform=timsp430"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\spackages", result.output)
    assert int(match.group(1)) > 1


def test_global_install_registry(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "64",
            "ArduinoJson@~6",
            "547@2.7.3",
            "AsyncMqttClient@<=0.8.2",
            "Adafruit PN532@1.3.2",
        ],
    )
    validate_cliresult(result)

    # install unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "install", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, UnknownPackageError)

    items1 = [d.basename for d in isolated_pio_core.join("lib").listdir()]
    items2 = [
        "ArduinoJson",
        f"ArduinoJson@{ARDUINO_JSON_VERSION}",
        "NeoPixelBus",
        "AsyncMqttClient",
        "ESPAsyncTCP",
        "AsyncTCP",
        "Adafruit PN532",
        "Adafruit BusIO",
    ]
    assert set(items1) == set(items2)


def test_global_install_archive(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip",
            "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip@5.8.2",
            "SomeLib=https://dl.registry.platformio.org/download/milesburton/library/DallasTemperature/3.11.0/DallasTemperature-3.11.0.tar.gz",
            "https://github.com/Pedroalbuquerque/ESP32WebServer/archive/master.zip",
        ],
    )
    validate_cliresult(result)

    # incorrect requirements
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/bblanchon/ArduinoJson/archive/v5.8.2.zip@1.2.3",
        ],
    )
    assert result.exit_code != 0

    items1 = [d.basename for d in isolated_pio_core.join("lib").listdir()]
    items2 = [
        "ArduinoJson",
        "ArduinoJson@src-69ebddd821f771debe7ee734d3c7fa81",
        "SomeLib",
        "OneWire",
        "ESP32WebServer",
    ]
    assert set(items1) >= set(items2)


def test_global_install_repository(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/gioblu/PJON.git#3.0",
            "https://github.com/gioblu/PJON.git#6.2",
            "https://github.com/bblanchon/ArduinoJson.git",
            "https://github.com/platformio/platformio-libmirror.git",
            # "https://developer.mbed.org/users/simon/code/TextLCD/",
            "https://github.com/knolleary/pubsubclient#bef58148582f956dfa772687db80c44e2279a163",
        ],
    )
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_core.join("lib").listdir()]
    items2 = [
        "PJON",
        "PJON@src-79de467ebe19de18287becff0a1fb42d",
        "ArduinoJson@src-69ebddd821f771debe7ee734d3c7fa81",
        "platformio-libmirror",
        "PubSubClient",
    ]
    assert set(items1) >= set(items2)


def test_install_duplicates(  # pylint: disable=unused-argument
    clirunner, validate_cliresult, without_internet
):
    # registry
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://dl.registry.platformio.org/download/milesburton/library/DallasTemperature/3.11.0/DallasTemperature-3.11.0.tar.gz",
        ],
    )
    validate_cliresult(result)
    assert "is already installed" in result.output

    # archive
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "install",
            "https://github.com/Pedroalbuquerque/ESP32WebServer/archive/master.zip",
        ],
    )
    validate_cliresult(result)
    assert "is already installed" in result.output

    # repository
    result = clirunner.invoke(
        cmd_lib,
        ["-g", "install", "https://github.com/platformio/platformio-libmirror.git"],
    )
    validate_cliresult(result)
    assert "is already installed" in result.output


def test_global_lib_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["-g", "list"])
    validate_cliresult(result)
    assert all(
        n in result.output
        for n in (
            "required: https://github.com/Pedroalbuquerque/ESP32WebServer/archive/master.zip",
            f"ArduinoJson @ {ARDUINO_JSON_VERSION}",
            "required: git+https://github.com/gioblu/PJON.git#3.0",
            "PJON @ 3.0.0+sha.1fb26f",
        )
    ), result.output

    result = clirunner.invoke(cmd_lib, ["-g", "list", "--json-output"])
    assert all(
        n in result.output
        for n in (
            "__pkg_dir",
            '"__src_url": "git+https://github.com/gioblu/PJON.git#6.2"',
            f'"version": "{ARDUINO_JSON_VERSION}"',
        )
    )
    items1 = [i["name"] for i in json.loads(result.output)]
    items2 = [
        "Adafruit BusIO",
        "Adafruit PN532",
        "ArduinoJson",
        "ArduinoJson",
        "ArduinoJson",
        "ArduinoJson",
        "AsyncMqttClient",
        "AsyncTCP",
        "DallasTemperature",
        "ESP32WebServer",
        "ESPAsyncTCP",
        "NeoPixelBus",
        "OneWire",
        "PJON",
        "PJON",
        "platformio-libmirror",
        "PubSubClient",
    ]
    assert sorted(items1) == sorted(items2)

    versions1 = [
        "{name}@{version}".format(**item) for item in json.loads(result.output)
    ]
    versions2 = [
        "ArduinoJson@5.8.2",
        f"ArduinoJson@{ARDUINO_JSON_VERSION}",
        "AsyncMqttClient@0.8.2",
        "NeoPixelBus@2.7.3",
        "PJON@6.2.0+sha.07fe9aa",
        "PJON@3.0.0+sha.1fb26fd",
        "PubSubClient@2.6.0+sha.bef5814",
        "Adafruit PN532@1.3.2",
    ]
    assert set(versions1) >= set(versions2)


def test_global_lib_update_check(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["-g", "update", "--dry-run", "--json-output"])
    validate_cliresult(result)
    output = json.loads(result.output)
    assert set(
        ["Adafruit PN532", "AsyncMqttClient", "ESPAsyncTCP", "NeoPixelBus"]
    ) == set(lib["name"] for lib in output)


def test_global_lib_update(clirunner, validate_cliresult):
    # update library using package directory
    result = clirunner.invoke(
        cmd_lib, ["-g", "update", "NeoPixelBus", "--dry-run", "--json-output"]
    )
    validate_cliresult(result)
    oudated = json.loads(result.output)
    assert len(oudated) == 1
    assert "__pkg_dir" in oudated[0]
    result = clirunner.invoke(cmd_lib, ["-g", "update", oudated[0]["__pkg_dir"]])
    validate_cliresult(result)
    assert "Removing NeoPixelBus @ 2.7.3" in strip_ansi_codes(result.output)

    # update all libraries
    result = clirunner.invoke(
        cmd_lib,
        ["-g", "update", "adafruit/Adafruit PN532", "marvinroger/AsyncMqttClient"],
    )
    validate_cliresult(result)

    # update unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "update", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, UnknownPackageError)


def test_global_lib_uninstall(clirunner, validate_cliresult, isolated_pio_core):
    # uninstall using package directory
    result = clirunner.invoke(cmd_lib, ["-g", "list", "--json-output"])
    validate_cliresult(result)
    items = json.loads(result.output)
    items = sorted(items, key=lambda item: item["__pkg_dir"])
    result = clirunner.invoke(cmd_lib, ["-g", "uninstall", items[0]["__pkg_dir"]])
    validate_cliresult(result)
    assert "Removing %s" % items[0]["name"] in strip_ansi_codes(result.output)

    # uninstall the rest libraries
    result = clirunner.invoke(
        cmd_lib,
        [
            "-g",
            "uninstall",
            "OneWire",
            "https://github.com/bblanchon/ArduinoJson.git",
            "ArduinoJson@!=5.6.7",
            "Adafruit PN532",
        ],
    )
    validate_cliresult(result)

    items1 = [d.basename for d in isolated_pio_core.join("lib").listdir()]
    items2 = [
        "AsyncMqttClient",
        "platformio-libmirror",
        "PubSubClient",
        "ArduinoJson@src-69ebddd821f771debe7ee734d3c7fa81",
        "ESPAsyncTCP@1.2.0",
        "AsyncTCP",
        "ArduinoJson",
        "ESPAsyncTCP",
        "ESP32WebServer",
        "PJON",
        "NeoPixelBus",
        "PJON@src-79de467ebe19de18287becff0a1fb42d",
        "SomeLib",
    ]
    assert set(items1) == set(items2)

    # uninstall unknown library
    result = clirunner.invoke(cmd_lib, ["-g", "uninstall", "Unknown"])
    assert result.exit_code != 0
    assert isinstance(result.exception, UnknownPackageError)


def test_lib_show(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["show", "64"])
    validate_cliresult(result)
    assert all(s in result.output for s in ("ArduinoJson", "Arduino"))
    result = clirunner.invoke(cmd_lib, ["show", "OneWire", "--json-output"])
    validate_cliresult(result)
    assert "OneWire" in result.output


def test_lib_builtin(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["builtin"])
    validate_cliresult(result)
    result = clirunner.invoke(cmd_lib, ["builtin", "--json-output"])
    validate_cliresult(result)


def test_lib_stats(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_lib, ["stats", "--json-output"])
    validate_cliresult(result)
    assert set(
        [
            "dlweek",
            "added",
            "updated",
            "topkeywords",
            "dlmonth",
            "dlday",
            "lastkeywords",
        ]
    ) == set(json.loads(result.output).keys())
