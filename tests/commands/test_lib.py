# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

import re

from platformio.commands.lib import cli


def test_search(clirunner, validate_cliresult):
    result = clirunner.invoke(cli, ["search", "DHT22"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) > 2

    result = clirunner.invoke(cli, ["search", "DHT22", "--platform=timsp430"])
    validate_cliresult(result)
    match = re.search(r"Found\s+(\d+)\slibraries:", result.output)
    assert int(match.group(1)) == 1


def test_global_install_registry(clirunner, validate_cliresult,
                                 isolated_pio_home):
    result = clirunner.invoke(
        cli, ["-g", "install", "58", "OneWire", "Json@5.4.0", "Json@>5.4"])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = ["DHT22_ID58", "Json_ID64", "Json_ID64@5.4.0", "OneWire_ID1"]
    assert set(items1) == set(items2)


def test_global_install_repository(clirunner, validate_cliresult,
                                   isolated_pio_home):
    result = clirunner.invoke(
        cli, ["-g", "install", "https://github.com/gioblu/PJON.git#3.0",
              "https://developer.mbed.org/users/simon/code/TextLCD/",
              "http://dl.platformio.org/libraries/archives/3/3756.tar.gz",
              "knolleary/pubsubclient"])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = ["PJON", "TextLCD", "ESPAsyncTCP", "PubSubClient"]
    assert set(items2) & set(items1)


def test_global_lib_list(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli, ["-g", "list"])
    validate_cliresult(result)
    assert all([n in result.output for n in ("OneWire", "DHT22", "64")])

    result = clirunner.invoke(cli, ["-g", "list", "--json-output"])
    validate_cliresult(result)
    assert all(
        [n in result.output
         for n in ("PJON",
                   "https://developer.mbed.org/users/simon/code/TextLCD/")])


def test_global_lib_show(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli, ["-g", "show", "64@5.4.0"])
    validate_cliresult(result)
    assert all(
        [s in result.output for s in ("Json", "arduino", "atmelavr", "5.4.0")])

    result = clirunner.invoke(cli, ["-g", "show", "Json@>5.4.0"])
    validate_cliresult(result)
    assert all([s in result.output for s in ("Json", "arduino", "atmelavr")])
    assert "5.4.0" not in result.output

    result = clirunner.invoke(cli, ["-g", "show", "1"])
    validate_cliresult(result)
    assert "OneWire" in result.output


def test_global_lib_update(clirunner, validate_cliresult, isolated_pio_home):
    result = clirunner.invoke(cli, ["-g", "update"])
    validate_cliresult(result)
    assert all([s in result.output for s in ("Up-to-date", "Checking")])


def test_global_lib_uninstall(clirunner, validate_cliresult,
                              isolated_pio_home):
    result = clirunner.invoke(
        cli, ["-g", "uninstall", "1", "Json@!=5.4.0", "TextLCD"])
    validate_cliresult(result)
    items1 = [d.basename for d in isolated_pio_home.join("lib").listdir()]
    items2 = ["DHT22_ID58", "Json_ID64@5.4.0", "ESPAsyncTCP_ID305",
              "pubsubclient", "PJON"]
    assert set(items1) == set(items2)
