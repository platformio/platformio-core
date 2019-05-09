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

import os

from platformio.project.config import ProjectConfig

BASE_CONFIG = """
[platformio]
env_default = base, extra_2
extra_configs =
  extra_envs.ini
  extra_debug.ini

# global options per [env:*]
[env]
monitor_speed = 115200
lib_deps = Lib1, Lib2
lib_ignore = ${custom.lib_ignore}

[custom]
debug_flags = -D RELEASE
lib_flags = -lc -lm
extra_flags = ${sysenv.__PIO_TEST_CNF_EXTRA_FLAGS}
lib_ignore = LibIgnoreCustom

[env:base]
build_flags = ${custom.debug_flags} ${custom.extra_flags}
"""

EXTRA_ENVS_CONFIG = """
[env:extra_1]
build_flags = ${custom.lib_flags} ${custom.debug_flags}

[env:extra_2]
build_flags = ${custom.debug_flags} ${custom.extra_flags}
lib_ignore = ${env.lib_ignore}, Lib3
"""

EXTRA_DEBUG_CONFIG = """
# Override original "custom.debug_flags"
[custom]
debug_flags = -D DEBUG=1

[env:extra_2]
build_flags = -Og
"""


def test_parser(tmpdir):
    tmpdir.join("platformio.ini").write(BASE_CONFIG)
    tmpdir.join("extra_envs.ini").write(EXTRA_ENVS_CONFIG)
    tmpdir.join("extra_debug.ini").write(EXTRA_DEBUG_CONFIG)

    config = None
    with tmpdir.as_cwd():
        config = ProjectConfig(tmpdir.join("platformio.ini").strpath)
    assert config

    # sections
    assert config.sections() == [
        "platformio", "env", "custom", "env:base", "env:extra_1", "env:extra_2"
    ]

    # envs
    assert config.envs() == ["base", "extra_1", "extra_2"]
    assert config.default_envs() == ["base", "extra_2"]

    # options
    assert config.options(env="base") == [
        "build_flags", "monitor_speed", "lib_deps", "lib_ignore"
    ]

    # has_option
    assert config.has_option("env:base", "monitor_speed")
    assert not config.has_option("custom", "monitor_speed")

    # sysenv
    assert config.get("custom", "extra_flags") == ""
    os.environ["__PIO_TEST_CNF_EXTRA_FLAGS"] = "-L /usr/local/lib"
    assert config.get("custom", "extra_flags") == "-L /usr/local/lib"

    # get
    assert config.get("custom", "debug_flags") == "-D DEBUG=1"
    assert config.get("env:extra_1", "build_flags") == "-lc -lm -D DEBUG=1"
    assert config.get("env:extra_2", "build_flags") == "-Og"
    assert config.get("env:extra_2", "monitor_speed") == "115200"
    assert config.get("env:base",
                      "build_flags") == ("-D DEBUG=1 -L /usr/local/lib")

    # items
    assert config.items("custom") == [("debug_flags", "-D DEBUG=1"),
                                      ("lib_flags", "-lc -lm"),
                                      ("extra_flags", "-L /usr/local/lib"),
                                      ("lib_ignore", "LibIgnoreCustom")]
    assert config.items(env="extra_1") == [("build_flags",
                                            "-lc -lm -D DEBUG=1"),
                                           ("monitor_speed", "115200"),
                                           ("lib_deps", "Lib1, Lib2"),
                                           ("lib_ignore", "LibIgnoreCustom")]
    assert config.items(env="extra_2") == [("build_flags", "-Og"),
                                           ("lib_ignore",
                                            "LibIgnoreCustom, Lib3"),
                                           ("monitor_speed", "115200"),
                                           ("lib_deps", "Lib1, Lib2")]
