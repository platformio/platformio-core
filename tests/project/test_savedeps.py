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

[env:bare]

[env:release]
platform = platformio/atmelavr
lib_deps =
    milesburton/DallasTemperature@^3.8

[env:debug]
platform = platformio/atmelavr@^3.4.0
lib_deps =
    ${env.lib_deps}
    milesburton/DallasTemperature@^3.9.1
    bblanchon/ArduinoJson
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

    # add to the sepcified environment
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
