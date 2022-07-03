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

from platformio.package.meta import PackageSpec
from platformio.project.config import ProjectConfig
from platformio.project.savedeps import save_project_dependencies

PROJECT_CONFIG_TPL = """
[env]
board = uno
framework = arduino
lib_deps =
    SPI
platform_packages =
    platformio/tool-jlink@^1.75001.0

[env:bare]

[env:release]
platform = platformio/espressif32
lib_deps =
    milesburton/DallasTemperature@^3.8

[env:debug]
platform = platformio/espressif32@^3.4.0
lib_deps =
    ${env.lib_deps}
    milesburton/DallasTemperature@^3.9.1
    bblanchon/ArduinoJson
platform_packages =
    ${env.platform_packages}
    platformio/framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git
"""


def test_save_libraries(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    specs = [
        PackageSpec("milesburton/DallasTemperature@^3.9"),
        PackageSpec("adafruit/Adafruit GPS Library@^1.6.0"),
        PackageSpec("https://github.com/nanopb/nanopb.git"),
    ]

    # add to the specified environment
    save_project_dependencies(
        str(project_dir), specs, scope="lib_deps", action="add", environments=["debug"]
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "lib_deps") == [
        "SPI",
        "bblanchon/ArduinoJson",
        "milesburton/DallasTemperature@^3.9",
        "adafruit/Adafruit GPS Library@^1.6.0",
        "https://github.com/nanopb/nanopb.git",
    ]
    assert config.get("env:bare", "lib_deps") == ["SPI"]
    assert config.get("env:release", "lib_deps") == [
        "milesburton/DallasTemperature@^3.8"
    ]

    # add to the the all environments
    save_project_dependencies(str(project_dir), specs, scope="lib_deps", action="add")
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "lib_deps") == [
        "SPI",
        "bblanchon/ArduinoJson",
        "milesburton/DallasTemperature@^3.9",
        "adafruit/Adafruit GPS Library@^1.6.0",
        "https://github.com/nanopb/nanopb.git",
    ]
    assert config.get("env:bare", "lib_deps") == [
        "milesburton/DallasTemperature@^3.9",
        "adafruit/Adafruit GPS Library@^1.6.0",
        "https://github.com/nanopb/nanopb.git",
    ]
    assert config.get("env:release", "lib_deps") == [
        "milesburton/DallasTemperature@^3.9",
        "adafruit/Adafruit GPS Library@^1.6.0",
        "https://github.com/nanopb/nanopb.git",
    ]

    # remove deps from env
    save_project_dependencies(
        str(project_dir),
        [PackageSpec("milesburton/DallasTemperature")],
        scope="lib_deps",
        action="remove",
        environments=["release"],
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:release", "lib_deps") == [
        "adafruit/Adafruit GPS Library@^1.6.0",
        "https://github.com/nanopb/nanopb.git",
    ]
    # invalid requirements
    save_project_dependencies(
        str(project_dir),
        [PackageSpec("adafruit/Adafruit GPS Library@^9.9.9")],
        scope="lib_deps",
        action="remove",
        environments=["release"],
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:release", "lib_deps") == [
        "https://github.com/nanopb/nanopb.git",
    ]

    # remove deps from all envs
    save_project_dependencies(
        str(project_dir), specs, scope="lib_deps", action="remove"
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "lib_deps") == [
        "SPI",
        "bblanchon/ArduinoJson",
    ]
    assert config.get("env:bare", "lib_deps") == ["SPI"]
    assert config.get("env:release", "lib_deps") == ["SPI"]


def test_save_tools(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_CONFIG_TPL)
    specs = [
        PackageSpec("platformio/framework-espidf@^2"),
        PackageSpec("platformio/tool-esptoolpy"),
    ]

    # add to the specified environment
    save_project_dependencies(
        str(project_dir),
        specs,
        scope="platform_packages",
        action="add",
        environments=["debug"],
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0",
        "platformio/framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git",
        "platformio/framework-espidf@^2",
        "platformio/tool-esptoolpy",
    ]
    assert config.get("env:bare", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0"
    ]
    assert config.get("env:release", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0"
    ]

    # add to the the all environments
    save_project_dependencies(
        str(project_dir), specs, scope="platform_packages", action="add"
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0",
        "platformio/framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git",
        "platformio/framework-espidf@^2",
        "platformio/tool-esptoolpy",
    ]
    assert config.get("env:bare", "platform_packages") == [
        "platformio/framework-espidf@^2",
        "platformio/tool-esptoolpy",
    ]
    assert config.get("env:release", "platform_packages") == [
        "platformio/framework-espidf@^2",
        "platformio/tool-esptoolpy",
    ]

    # remove deps from env
    save_project_dependencies(
        str(project_dir),
        [PackageSpec("platformio/framework-espidf")],
        scope="platform_packages",
        action="remove",
        environments=["release"],
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:release", "platform_packages") == [
        "platformio/tool-esptoolpy",
    ]
    # invalid requirements
    save_project_dependencies(
        str(project_dir),
        [PackageSpec("platformio/tool-esptoolpy@9.9.9")],
        scope="platform_packages",
        action="remove",
        environments=["release"],
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:release", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0",
    ]

    # remove deps from all envs
    save_project_dependencies(
        str(project_dir), specs, scope="platform_packages", action="remove"
    )
    config = ProjectConfig.get_instance(str(project_dir / "platformio.ini"))
    assert config.get("env:debug", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0",
        "platformio/framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git",
    ]
    assert config.get("env:bare", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0"
    ]
    assert config.get("env:release", "platform_packages") == [
        "platformio/tool-jlink@^1.75001.0"
    ]
