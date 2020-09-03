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

import semantic_version

from platformio.clients.registry import RegistryClient
from platformio.commands.lib.command import cli as cmd_lib
from platformio.package.meta import PackageType
from platformio.package.vcsclient import VCSClientFactory
from platformio.project.config import ProjectConfig


def test_saving_deps(clirunner, validate_cliresult, isolated_pio_core, tmpdir_factory):
    regclient = RegistryClient()
    project_dir = tmpdir_factory.mktemp("project")
    project_dir.join("platformio.ini").write(
        """
[env]
lib_deps = ArduinoJson

[env:one]
board = devkit

[env:two]
framework = foo
lib_deps =
    CustomLib
    ArduinoJson @ 5.10.1
"""
    )
    result = clirunner.invoke(
        cmd_lib,
        ["-d", str(project_dir), "install", "64", "knolleary/PubSubClient@~2.7"],
    )
    validate_cliresult(result)
    aj_pkg_data = regclient.get_package(PackageType.LIBRARY, "bblanchon", "ArduinoJson")
    config = ProjectConfig(os.path.join(str(project_dir), "platformio.ini"))
    assert sorted(config.get("env:one", "lib_deps")) == sorted(
        [
            "bblanchon/ArduinoJson@^%s" % aj_pkg_data["version"]["name"],
            "knolleary/PubSubClient@~2.7",
        ]
    )
    assert sorted(config.get("env:two", "lib_deps")) == sorted(
        [
            "CustomLib",
            "bblanchon/ArduinoJson@^%s" % aj_pkg_data["version"]["name"],
            "knolleary/PubSubClient@~2.7",
        ]
    )

    # ensure "build" version without NPM spec
    result = clirunner.invoke(
        cmd_lib,
        ["-d", str(project_dir), "-e", "one", "install", "mbed-sam-grove/LinkedList"],
    )
    validate_cliresult(result)
    ll_pkg_data = regclient.get_package(
        PackageType.LIBRARY, "mbed-sam-grove", "LinkedList"
    )
    config = ProjectConfig(os.path.join(str(project_dir), "platformio.ini"))
    assert sorted(config.get("env:one", "lib_deps")) == sorted(
        [
            "bblanchon/ArduinoJson@^%s" % aj_pkg_data["version"]["name"],
            "knolleary/PubSubClient@~2.7",
            "mbed-sam-grove/LinkedList@%s" % ll_pkg_data["version"]["name"],
        ]
    )

    # check external package via Git repo
    result = clirunner.invoke(
        cmd_lib,
        [
            "-d",
            str(project_dir),
            "-e",
            "one",
            "install",
            "https://github.com/OttoWinter/async-mqtt-client.git#v0.8.3 @ 0.8.3",
        ],
    )
    validate_cliresult(result)
    config = ProjectConfig(os.path.join(str(project_dir), "platformio.ini"))
    assert len(config.get("env:one", "lib_deps")) == 4
    assert config.get("env:one", "lib_deps")[3] == (
        "https://github.com/OttoWinter/async-mqtt-client.git#v0.8.3 @ 0.8.3"
    )

    # test uninstalling
    # from all envs
    result = clirunner.invoke(
        cmd_lib, ["-d", str(project_dir), "uninstall", "ArduinoJson"]
    )
    validate_cliresult(result)
    # from "one" env
    result = clirunner.invoke(
        cmd_lib,
        [
            "-d",
            str(project_dir),
            "-e",
            "one",
            "uninstall",
            "knolleary/PubSubClient@~2.7",
        ],
    )
    validate_cliresult(result)
    config = ProjectConfig(os.path.join(str(project_dir), "platformio.ini"))
    assert len(config.get("env:one", "lib_deps")) == 2
    assert len(config.get("env:two", "lib_deps")) == 2
    assert config.get("env:one", "lib_deps") == [
        "mbed-sam-grove/LinkedList@%s" % ll_pkg_data["version"]["name"],
        "https://github.com/OttoWinter/async-mqtt-client.git#v0.8.3 @ 0.8.3",
    ]
    assert config.get("env:two", "lib_deps") == [
        "CustomLib",
        "knolleary/PubSubClient@~2.7",
    ]

    # test list
    result = clirunner.invoke(cmd_lib, ["-d", str(project_dir), "list"])
    validate_cliresult(result)
    assert "Version: 0.8.3+sha." in result.stdout
    assert (
        "Source: git+https://github.com/OttoWinter/async-mqtt-client.git#v0.8.3"
        in result.stdout
    )
    result = clirunner.invoke(
        cmd_lib, ["-d", str(project_dir), "list", "--json-output"]
    )
    validate_cliresult(result)
    data = {}
    for key, value in json.loads(result.stdout).items():
        data[os.path.basename(key)] = value
    ame_lib = next(
        item for item in data["one"] if item["name"] == "AsyncMqttClient-esphome"
    )
    ame_vcs = VCSClientFactory.new(ame_lib["__pkg_dir"], ame_lib["__src_url"])
    assert len(data["two"]) == 1
    assert data["two"][0]["name"] == "PubSubClient"
    assert "__pkg_dir" in data["one"][0]
    assert (
        ame_lib["__src_url"]
        == "git+https://github.com/OttoWinter/async-mqtt-client.git#v0.8.3"
    )
    assert ame_lib["version"] == ("0.8.3+sha.%s" % ame_vcs.get_current_revision())


def test_update(clirunner, validate_cliresult, isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("test-updates")
    result = clirunner.invoke(
        cmd_lib,
        ["-d", str(storage_dir), "install", "ArduinoJson @ 5.10.1", "Blynk @ ~0.5.0"],
    )
    validate_cliresult(result)
    result = clirunner.invoke(
        cmd_lib, ["-d", str(storage_dir), "update", "--dry-run", "--json-output"]
    )
    validate_cliresult(result)
    outdated = json.loads(result.stdout)
    assert len(outdated) == 2
    # ArduinoJson
    assert outdated[0]["version"] == "5.10.1"
    assert outdated[0]["versionWanted"] is None
    assert semantic_version.Version(
        outdated[0]["versionLatest"]
    ) > semantic_version.Version("6.16.0")
    # Blynk
    assert outdated[1]["version"] == "0.5.4"
    assert outdated[1]["versionWanted"] is None
    assert semantic_version.Version(
        outdated[1]["versionLatest"]
    ) > semantic_version.Version("0.6.0")

    # check with spec
    result = clirunner.invoke(
        cmd_lib,
        [
            "-d",
            str(storage_dir),
            "update",
            "--dry-run",
            "--json-output",
            "ArduinoJson @ ^5",
        ],
    )
    validate_cliresult(result)
    outdated = json.loads(result.stdout)
    assert outdated[0]["version"] == "5.10.1"
    assert outdated[0]["versionWanted"] == "5.13.4"
    assert semantic_version.Version(
        outdated[0]["versionLatest"]
    ) > semantic_version.Version("6.16.0")
    # update with spec
    result = clirunner.invoke(
        cmd_lib, ["-d", str(storage_dir), "update", "--silent", "ArduinoJson @ ^5.10.1"]
    )
    validate_cliresult(result)
    result = clirunner.invoke(
        cmd_lib, ["-d", str(storage_dir), "list", "--json-output"]
    )
    validate_cliresult(result)
    items = json.loads(result.stdout)
    assert len(items) == 2
    assert items[0]["version"] == "5.13.4"
    assert items[1]["version"] == "0.5.4"

    # Check incompatible
    result = clirunner.invoke(
        cmd_lib, ["-d", str(storage_dir), "update", "--dry-run", "ArduinoJson @ ^5"]
    )
    validate_cliresult(result)
    assert "Incompatible" in result.stdout
