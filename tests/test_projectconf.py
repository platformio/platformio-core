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

# pylint: disable=redefined-outer-name

import os

import pytest

from platformio.project.config import ConfigParser, ProjectConfig
from platformio.project.exception import InvalidProjectConfError, UnknownEnvNamesError

BASE_CONFIG = """
[platformio]
env_default = base, extra_2
extra_configs =
  extra_envs.ini
  extra_debug.ini

# global options per [env:*]
[env]
monitor_speed = 9600  ; inline comment
custom_monitor_speed = 115200
lib_deps =
    Lib1 ; inline comment in multi-line value
    Lib2
lib_ignore = ${custom.lib_ignore}
custom_builtin_option = ${env.build_type}

[strict_ldf]
lib_ldf_mode = chain+
lib_compat_mode = strict

[monitor_custom]
monitor_speed = ${env.custom_monitor_speed}

[strict_settings]
extends = strict_ldf, monitor_custom
build_flags = -D RELEASE

[custom]
debug_flags = -D RELEASE
lib_flags = -lc -lm
extra_flags = ${sysenv.__PIO_TEST_CNF_EXTRA_FLAGS}
lib_ignore = LibIgnoreCustom

[env:base]
build_flags = ${custom.debug_flags} ${custom.extra_flags}
lib_compat_mode = ${strict_ldf.lib_compat_mode}
targets =

[env:test_extends]
extends = strict_settings


"""

EXTRA_ENVS_CONFIG = """
[env:extra_1]
build_flags =
    -fdata-sections
    -Wl,--gc-sections
    ${custom.lib_flags}
    ${custom.debug_flags}
lib_install = 574

[env:extra_2]
build_flags = ${custom.debug_flags} ${custom.extra_flags}
lib_ignore = ${env.lib_ignore}, Lib3
upload_port = /dev/extra_2/port
"""

EXTRA_DEBUG_CONFIG = """
# Override original "custom.debug_flags"
[custom]
debug_flags = -D DEBUG=1

[env:extra_2]
build_flags = -Og
"""


@pytest.fixture(scope="module")
def config(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(BASE_CONFIG)
    tmpdir.join("extra_envs.ini").write(EXTRA_ENVS_CONFIG)
    tmpdir.join("extra_debug.ini").write(EXTRA_DEBUG_CONFIG)
    with tmpdir.as_cwd():
        return ProjectConfig(tmpdir.join("platformio.ini").strpath)


def test_empty_config():
    config = ProjectConfig("/non/existing/platformio.ini")
    # unknown section
    with pytest.raises(InvalidProjectConfError):
        config.get("unknown_section", "unknown_option")
    assert config.sections() == []
    assert config.get("section", "option", 13) == 13


def test_warnings(config):
    config.validate(["extra_2", "base"], silent=True)
    assert len(config.warnings) == 2
    assert "lib_install" in config.warnings[1]

    with pytest.raises(UnknownEnvNamesError):
        config.validate(["non-existing-env"])


def test_defaults(config):
    assert config.get_optional_dir("core") == os.path.join(
        os.path.expanduser("~"), ".platformio"
    )
    assert config.get("strict_ldf", "lib_deps", ["Empty"]) == ["Empty"]
    assert config.get("env:extra_2", "lib_compat_mode") == "soft"
    assert config.get("env:extra_2", "build_type") == "release"
    assert config.get("env:extra_2", "build_type", None) is None
    assert config.get("env:extra_2", "lib_archive", "no") is False

    config.expand_interpolations = False
    with pytest.raises(
        InvalidProjectConfError, match="No option 'lib_deps' in section: 'strict_ldf'"
    ):
        assert config.get("strict_ldf", "lib_deps", ["Empty"]) == ["Empty"]
    config.expand_interpolations = True


def test_sections(config):
    with pytest.raises(ConfigParser.NoSectionError):
        config.getraw("unknown_section", "unknown_option")

    assert config.sections() == [
        "platformio",
        "env",
        "strict_ldf",
        "monitor_custom",
        "strict_settings",
        "custom",
        "env:base",
        "env:test_extends",
        "env:extra_1",
        "env:extra_2",
    ]


def test_envs(config):
    assert config.envs() == ["base", "test_extends", "extra_1", "extra_2"]
    assert config.default_envs() == ["base", "extra_2"]


def test_options(config):
    assert config.options(env="base") == [
        "build_flags",
        "lib_compat_mode",
        "targets",
        "monitor_speed",
        "custom_monitor_speed",
        "lib_deps",
        "lib_ignore",
        "custom_builtin_option",
    ]
    assert config.options(env="test_extends") == [
        "extends",
        "build_flags",
        "lib_ldf_mode",
        "lib_compat_mode",
        "monitor_speed",
        "custom_monitor_speed",
        "lib_deps",
        "lib_ignore",
        "custom_builtin_option",
    ]


def test_has_option(config):
    assert config.has_option("env:base", "monitor_speed")
    assert not config.has_option("custom", "monitor_speed")
    assert not config.has_option("env:extra_1", "lib_install")
    assert config.has_option("env:test_extends", "lib_compat_mode")


def test_sysenv_options(config):
    assert config.getraw("custom", "extra_flags") == ""
    assert config.get("env:base", "build_flags") == ["-D DEBUG=1"]
    assert config.get("env:base", "upload_port") is None
    assert config.get("env:extra_2", "upload_port") == "/dev/extra_2/port"
    os.environ["PLATFORMIO_BUILD_FLAGS"] = "-DSYSENVDEPS1 -DSYSENVDEPS2"
    os.environ["PLATFORMIO_BUILD_UNFLAGS"] = "-DREMOVE_MACRO"
    os.environ["PLATFORMIO_UPLOAD_PORT"] = "/dev/sysenv/port"
    os.environ["__PIO_TEST_CNF_EXTRA_FLAGS"] = "-L /usr/local/lib"
    assert config.get("custom", "extra_flags") == "-L /usr/local/lib"
    assert config.get("env:base", "build_flags") == [
        "-D DEBUG=1 -L /usr/local/lib",
        "-DSYSENVDEPS1 -DSYSENVDEPS2",
    ]
    assert config.get("env:base", "upload_port") == "/dev/sysenv/port"
    assert config.get("env:extra_2", "upload_port") == "/dev/extra_2/port"
    assert config.get("env:base", "build_unflags") == ["-DREMOVE_MACRO"]

    # env var as option
    assert config.options(env="test_extends") == [
        "extends",
        "build_flags",
        "lib_ldf_mode",
        "lib_compat_mode",
        "monitor_speed",
        "custom_monitor_speed",
        "lib_deps",
        "lib_ignore",
        "custom_builtin_option",
        "build_unflags",
        "upload_port",
    ]

    # sysenv
    os.environ["PLATFORMIO_HOME_DIR"] = "/custom/core/dir"
    assert config.get("platformio", "core_dir") == "/custom/core/dir"

    # cleanup system environment variables
    del os.environ["PLATFORMIO_BUILD_FLAGS"]
    del os.environ["PLATFORMIO_BUILD_UNFLAGS"]
    del os.environ["PLATFORMIO_UPLOAD_PORT"]
    del os.environ["__PIO_TEST_CNF_EXTRA_FLAGS"]
    del os.environ["PLATFORMIO_HOME_DIR"]


def test_getraw_value(config):
    # unknown option
    with pytest.raises(ConfigParser.NoOptionError):
        config.getraw("custom", "unknown_option")
    # unknown option even if exists in [env]
    with pytest.raises(ConfigParser.NoOptionError):
        config.getraw("platformio", "monitor_speed")

    # default
    assert config.getraw("unknown", "option", "default") == "default"
    assert config.getraw("env:base", "custom_builtin_option") == "release"

    # known
    assert config.getraw("env:base", "targets") == ""
    assert config.getraw("env:extra_1", "lib_deps") == "574"
    assert (
        config.getraw("env:extra_1", "build_flags")
        == "\n-fdata-sections\n-Wl,--gc-sections\n-lc -lm\n-D DEBUG=1"
    )

    # extended
    assert config.getraw("env:test_extends", "lib_ldf_mode") == "chain+"
    assert config.getraw("env", "monitor_speed") == "9600"
    assert config.getraw("env:test_extends", "monitor_speed") == "115200"


def test_get_value(config):
    assert config.get("custom", "debug_flags") == "-D DEBUG=1"
    assert config.get("env:extra_1", "build_flags") == [
        "-fdata-sections",
        "-Wl,--gc-sections",
        "-lc -lm",
        "-D DEBUG=1",
    ]
    assert config.get("env:extra_2", "build_flags") == ["-Og"]
    assert config.get("env:extra_2", "monitor_speed") == 9600
    assert config.get("env:base", "build_flags") == ["-D DEBUG=1"]


def test_items(config):
    assert config.items("custom") == [
        ("debug_flags", "-D DEBUG=1"),
        ("lib_flags", "-lc -lm"),
        ("extra_flags", ""),
        ("lib_ignore", "LibIgnoreCustom"),
    ]
    assert config.items(env="base") == [
        ("build_flags", ["-D DEBUG=1"]),
        ("lib_compat_mode", "strict"),
        ("targets", []),
        ("monitor_speed", 9600),
        ("custom_monitor_speed", "115200"),
        ("lib_deps", ["Lib1", "Lib2"]),
        ("lib_ignore", ["LibIgnoreCustom"]),
        ("custom_builtin_option", "release"),
    ]
    assert config.items(env="extra_1") == [
        (
            "build_flags",
            ["-fdata-sections", "-Wl,--gc-sections", "-lc -lm", "-D DEBUG=1"],
        ),
        ("lib_deps", ["574"]),
        ("monitor_speed", 9600),
        ("custom_monitor_speed", "115200"),
        ("lib_ignore", ["LibIgnoreCustom"]),
        ("custom_builtin_option", "release"),
    ]
    assert config.items(env="extra_2") == [
        ("build_flags", ["-Og"]),
        ("lib_ignore", ["LibIgnoreCustom", "Lib3"]),
        ("upload_port", "/dev/extra_2/port"),
        ("monitor_speed", 9600),
        ("custom_monitor_speed", "115200"),
        ("lib_deps", ["Lib1", "Lib2"]),
        ("custom_builtin_option", "release"),
    ]
    assert config.items(env="test_extends") == [
        ("extends", ["strict_settings"]),
        ("build_flags", ["-D RELEASE"]),
        ("lib_ldf_mode", "chain+"),
        ("lib_compat_mode", "strict"),
        ("monitor_speed", 115200),
        ("custom_monitor_speed", "115200"),
        ("lib_deps", ["Lib1", "Lib2"]),
        ("lib_ignore", ["LibIgnoreCustom"]),
        ("custom_builtin_option", "release"),
    ]


def test_update_and_save(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(
        """
[platformio]
extra_configs = a.ini, b.ini

[env:myenv]
board = myboard
    """
    )
    config = ProjectConfig(tmpdir.join("platformio.ini").strpath)
    assert config.envs() == ["myenv"]
    assert config.as_tuple()[0][1][0][1] == ["a.ini", "b.ini"]

    config.update(
        [
            ["platformio", [("extra_configs", ["extra.ini"])]],
            ["env:myenv", [("framework", ["espidf", "arduino"])]],
            ["check_types", [("float_option", 13.99), ("bool_option", True)]],
        ]
    )
    assert config.get("platformio", "extra_configs") == ["extra.ini"]
    config.remove_section("platformio")
    assert config.as_tuple() == [
        ("env:myenv", [("board", "myboard"), ("framework", ["espidf", "arduino"])]),
        ("check_types", [("float_option", "13.99"), ("bool_option", "yes")]),
    ]

    config.save()
    contents = tmpdir.join("platformio.ini").read()
    assert contents[-4:] == "yes\n"
    lines = [
        line.strip()
        for line in contents.split("\n")
        if line.strip() and not line.startswith((";", "#"))
    ]
    assert lines == [
        "[env:myenv]",
        "board = myboard",
        "framework =",
        "espidf",
        "arduino",
        "[check_types]",
        "float_option = 13.99",
        "bool_option = yes",
    ]


def test_update_and_clear(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(
        """
[platformio]
extra_configs = a.ini, b.ini

[env:myenv]
board = myboard
    """
    )
    config = ProjectConfig(tmpdir.join("platformio.ini").strpath)
    assert config.sections() == ["platformio", "env:myenv"]
    config.update([["mysection", [("opt1", "value1"), ("opt2", "value2")]]], clear=True)
    assert config.as_tuple() == [
        ("mysection", [("opt1", "value1"), ("opt2", "value2")])
    ]


def test_dump(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("project")
    tmpdir.join("platformio.ini").write(BASE_CONFIG)
    tmpdir.join("extra_envs.ini").write(EXTRA_ENVS_CONFIG)
    tmpdir.join("extra_debug.ini").write(EXTRA_DEBUG_CONFIG)
    config = ProjectConfig(
        tmpdir.join("platformio.ini").strpath,
        parse_extra=False,
        expand_interpolations=False,
    )
    assert config.as_tuple() == [
        (
            "platformio",
            [
                ("extra_configs", ["extra_envs.ini", "extra_debug.ini"]),
                ("default_envs", ["base", "extra_2"]),
            ],
        ),
        (
            "env",
            [
                ("monitor_speed", 9600),
                ("custom_monitor_speed", "115200"),
                ("lib_deps", ["Lib1", "Lib2"]),
                ("lib_ignore", ["${custom.lib_ignore}"]),
                ("custom_builtin_option", "${env.build_type}"),
            ],
        ),
        ("strict_ldf", [("lib_ldf_mode", "chain+"), ("lib_compat_mode", "strict")]),
        ("monitor_custom", [("monitor_speed", "${env.custom_monitor_speed}")]),
        (
            "strict_settings",
            [("extends", "strict_ldf, monitor_custom"), ("build_flags", "-D RELEASE")],
        ),
        (
            "custom",
            [
                ("debug_flags", "-D RELEASE"),
                ("lib_flags", "-lc -lm"),
                ("extra_flags", "${sysenv.__PIO_TEST_CNF_EXTRA_FLAGS}"),
                ("lib_ignore", "LibIgnoreCustom"),
            ],
        ),
        (
            "env:base",
            [
                ("build_flags", ["${custom.debug_flags} ${custom.extra_flags}"]),
                ("lib_compat_mode", "${strict_ldf.lib_compat_mode}"),
                ("targets", []),
            ],
        ),
        ("env:test_extends", [("extends", ["strict_settings"])]),
    ]
