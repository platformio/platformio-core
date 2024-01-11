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

import configparser
import os
import sys
from pathlib import Path

import pytest

from platformio import fs
from platformio.project.config import ProjectConfig
from platformio.project.exception import (
    InvalidEnvNameError,
    InvalidProjectConfError,
    UnknownEnvNamesError,
)

BASE_CONFIG = """
[platformio]
env_default = base, extra_2
src_dir = ${custom.src_dir}
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
src_dir = source
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

[env:inject_base_env]
debug_build_flags =
    ${env.debug_build_flags}
    -D CUSTOM_DEBUG_FLAG

"""

EXTRA_ENVS_CONFIG = """
[env:extra_1]
build_flags =
    -fdata-sections
    -Wl,--gc-sections
    ${custom.lib_flags}
    ${custom.debug_flags}
    -D SERIAL_BAUD_RATE=${this.monitor_speed}
lib_install = 574

[env:extra_2]
build_flags = ${custom.debug_flags} ${custom.extra_flags}
lib_ignore = ${env.lib_ignore}, Lib3
upload_port = /dev/extra_2/port
debug_server = ${custom.debug_server}
"""

EXTRA_DEBUG_CONFIG = """
# Override original "custom.debug_flags"
[custom]
debug_flags = -D DEBUG=1
debug_server =
    ${platformio.packages_dir}/tool-openocd/openocd
    --help
src_filter = -<*>
    +<a>
    +<b>

[env:extra_2]
build_flags = -Og
src_filter = ${custom.src_filter} +<c>
"""

DEFAULT_CORE_DIR = os.path.join(fs.expanduser("~"), ".platformio")


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
    assert len(config.warnings) == 3
    assert "lib_install" in config.warnings[1]

    with pytest.raises(UnknownEnvNamesError):
        config.validate(["non-existing-env"])


def test_defaults(config):
    assert config.get("platformio", "core_dir") == os.path.join(
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
    with pytest.raises(configparser.NoSectionError):
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
        "env:inject_base_env",
        "env:extra_1",
        "env:extra_2",
    ]


def test_envs(config):
    assert config.envs() == [
        "base",
        "test_extends",
        "inject_base_env",
        "extra_1",
        "extra_2",
    ]
    assert config.default_envs() == ["base", "extra_2"]
    assert config.get_default_env() == "base"


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
        "monitor_speed",
        "lib_ldf_mode",
        "lib_compat_mode",
        "custom_monitor_speed",
        "lib_deps",
        "lib_ignore",
        "custom_builtin_option",
    ]


def test_has_option(config):
    assert config.has_option("env:base", "monitor_speed")
    assert not config.has_option("custom", "monitor_speed")
    assert config.has_option("env:extra_1", "lib_install")
    assert config.has_option("env:test_extends", "lib_compat_mode")
    assert config.has_option("env:extra_2", "src_filter")


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
    assert config.get("env:extra_2", "upload_port") == "/dev/sysenv/port"
    assert config.get("env:base", "build_unflags") == ["-DREMOVE_MACRO"]

    # env var as option
    assert config.options(env="test_extends") == [
        "extends",
        "build_flags",
        "monitor_speed",
        "lib_ldf_mode",
        "lib_compat_mode",
        "custom_monitor_speed",
        "lib_deps",
        "lib_ignore",
        "custom_builtin_option",
        "build_unflags",
        "upload_port",
    ]

    # sysenv dirs
    custom_core_dir = os.path.join(os.getcwd(), "custom-core")
    custom_src_dir = os.path.join(os.getcwd(), "custom-src")
    custom_build_dir = os.path.join(os.getcwd(), "custom-build")
    os.environ["PLATFORMIO_HOME_DIR"] = custom_core_dir
    os.environ["PLATFORMIO_SRC_DIR"] = custom_src_dir
    os.environ["PLATFORMIO_BUILD_DIR"] = custom_build_dir
    assert os.path.realpath(config.get("platformio", "core_dir")) == os.path.realpath(
        custom_core_dir
    )
    assert os.path.realpath(config.get("platformio", "src_dir")) == os.path.realpath(
        custom_src_dir
    )
    assert os.path.realpath(config.get("platformio", "build_dir")) == os.path.realpath(
        custom_build_dir
    )

    # cleanup system environment variables
    del os.environ["PLATFORMIO_BUILD_FLAGS"]
    del os.environ["PLATFORMIO_BUILD_UNFLAGS"]
    del os.environ["PLATFORMIO_UPLOAD_PORT"]
    del os.environ["__PIO_TEST_CNF_EXTRA_FLAGS"]
    del os.environ["PLATFORMIO_HOME_DIR"]
    del os.environ["PLATFORMIO_SRC_DIR"]
    del os.environ["PLATFORMIO_BUILD_DIR"]


def test_getraw_value(config):
    # unknown option
    with pytest.raises(configparser.NoOptionError):
        config.getraw("custom", "unknown_option")
    # unknown option even if exists in [env]
    with pytest.raises(configparser.NoOptionError):
        config.getraw("platformio", "monitor_speed")

    # default
    assert config.getraw("unknown", "option", "default") == "default"
    assert config.getraw("env:base", "custom_builtin_option") == "release"

    # known
    assert config.getraw("env:base", "targets") == ""
    assert config.getraw("env:extra_1", "lib_deps") == "574"
    assert config.getraw("env:extra_1", "build_flags") == (
        "\n-fdata-sections\n-Wl,--gc-sections\n"
        "-lc -lm\n-D DEBUG=1\n-D SERIAL_BAUD_RATE=9600"
    )

    # extended
    assert config.getraw("env:test_extends", "lib_ldf_mode") == "chain+"
    assert config.getraw("env", "monitor_speed") == "9600"
    assert config.getraw("env:test_extends", "monitor_speed") == "115200"

    # dir options
    packages_dir = os.path.join(DEFAULT_CORE_DIR, "packages")
    assert config.get("platformio", "packages_dir") == packages_dir
    assert (
        config.getraw("custom", "debug_server")
        == f"\n{packages_dir}/tool-openocd/openocd\n--help"
    )

    # renamed option
    assert config.getraw("env:extra_1", "lib_install") == "574"
    assert config.getraw("env:extra_1", "lib_deps") == "574"
    assert config.getraw("env:base", "debug_load_cmd") == ["load"]


def test_get_value(config):
    assert config.get("custom", "debug_flags") == "-D DEBUG=1"
    assert config.get("env:extra_1", "build_flags") == [
        "-fdata-sections",
        "-Wl,--gc-sections",
        "-lc -lm",
        "-D DEBUG=1",
        "-D SERIAL_BAUD_RATE=9600",
    ]
    assert config.get("env:extra_2", "build_flags") == ["-Og"]
    assert config.get("env:extra_2", "monitor_speed") == 9600
    assert config.get("env:base", "build_flags") == ["-D DEBUG=1"]

    # get default value from ConfigOption
    assert config.get("env:inject_base_env", "debug_build_flags") == [
        "-Og",
        "-g2",
        "-ggdb2",
        "-D CUSTOM_DEBUG_FLAG",
    ]

    # dir options
    assert config.get("platformio", "packages_dir") == os.path.join(
        DEFAULT_CORE_DIR, "packages"
    )
    assert config.get("env:extra_2", "debug_server") == [
        os.path.join(DEFAULT_CORE_DIR, "packages/tool-openocd/openocd"),
        "--help",
    ]
    # test relative dir
    assert config.get("platformio", "src_dir") == os.path.abspath(
        os.path.join(os.getcwd(), "source")
    )

    # renamed option
    assert config.get("env:extra_1", "lib_install") == ["574"]
    assert config.get("env:extra_1", "lib_deps") == ["574"]
    assert config.get("env:base", "debug_load_cmd") == ["load"]


def test_items(config):
    assert config.items("custom") == [
        ("src_dir", "source"),
        ("debug_flags", "-D DEBUG=1"),
        ("lib_flags", "-lc -lm"),
        ("extra_flags", ""),
        ("lib_ignore", "LibIgnoreCustom"),
        (
            "debug_server",
            "\n%s/tool-openocd/openocd\n--help"
            % os.path.join(DEFAULT_CORE_DIR, "packages"),
        ),
        ("src_filter", "-<*>\n+<a>\n+<b>"),
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
            [
                "-fdata-sections",
                "-Wl,--gc-sections",
                "-lc -lm",
                "-D DEBUG=1",
                "-D SERIAL_BAUD_RATE=9600",
            ],
        ),
        ("lib_install", ["574"]),
        ("monitor_speed", 9600),
        ("custom_monitor_speed", "115200"),
        ("lib_deps", ["574"]),
        ("lib_ignore", ["LibIgnoreCustom"]),
        ("custom_builtin_option", "release"),
    ]
    assert config.items(env="extra_2") == [
        ("build_flags", ["-Og"]),
        ("lib_ignore", ["LibIgnoreCustom", "Lib3"]),
        ("upload_port", "/dev/extra_2/port"),
        (
            "debug_server",
            [
                "%s/tool-openocd/openocd" % os.path.join(DEFAULT_CORE_DIR, "packages"),
                "--help",
            ],
        ),
        ("src_filter", ["-<*>", "+<a>", "+<b> +<c>"]),
        ("monitor_speed", 9600),
        ("custom_monitor_speed", "115200"),
        ("lib_deps", ["Lib1", "Lib2"]),
        ("custom_builtin_option", "release"),
    ]
    assert config.items(env="test_extends") == [
        ("extends", ["strict_settings"]),
        ("build_flags", ["-D RELEASE"]),
        ("monitor_speed", 115200),
        ("lib_ldf_mode", "chain+"),
        ("lib_compat_mode", "strict"),
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
                ("env_default", ["base", "extra_2"]),
                ("src_dir", "${custom.src_dir}"),
                ("extra_configs", ["extra_envs.ini", "extra_debug.ini"]),
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
                ("src_dir", "source"),
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
        (
            "env:inject_base_env",
            [
                (
                    "debug_build_flags",
                    ["${env.debug_build_flags}", "-D CUSTOM_DEBUG_FLAG"],
                )
            ],
        ),
    ]


@pytest.mark.skipif(sys.platform != "win32", reason="runs only on windows")
def test_win_core_root_dir(tmpdir_factory):
    try:
        win_core_root_dir = os.path.splitdrive(fs.expanduser("~"))[0] + "\\.platformio"
        remove_dir_at_exit = False
        if not os.path.isdir(win_core_root_dir):
            remove_dir_at_exit = True
            os.makedirs(win_core_root_dir)

        # Default config
        config = ProjectConfig()
        assert config.get("platformio", "core_dir") == win_core_root_dir
        assert config.get("platformio", "packages_dir") == os.path.join(
            win_core_root_dir, "packages"
        )

        # Override in config
        tmpdir = tmpdir_factory.mktemp("project")
        tmpdir.join("platformio.ini").write(
            """
[platformio]
core_dir = ~/.pio
        """
        )
        config = ProjectConfig(tmpdir.join("platformio.ini").strpath)
        assert config.get("platformio", "core_dir") != win_core_root_dir
        assert config.get("platformio", "core_dir") == os.path.realpath(
            fs.expanduser("~/.pio")
        )

        if remove_dir_at_exit:
            fs.rmtree(win_core_root_dir)
    except PermissionError:
        pass


def test_this(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[common]
board = uno

[env:myenv]
extends = common
build_flags = -D${this.__env__}
custom_option = ${this.board}
    """
    )
    config = ProjectConfig(str(project_conf))
    assert config.get("env:myenv", "custom_option") == "uno"
    assert config.get("env:myenv", "build_flags") == ["-Dmyenv"]


def test_project_name(tmp_path: Path):
    project_dir = tmp_path / "my-project-name"
    project_dir.mkdir()
    project_conf = project_dir / "platformio.ini"
    project_conf.write_text(
        """
[env:myenv]
    """
    )
    with fs.cd(str(project_dir)):
        config = ProjectConfig(str(project_conf))
        assert config.get("platformio", "name") == "my-project-name"

    # custom name
    project_conf.write_text(
        """
[platformio]
name = custom-project-name
    """
    )
    config = ProjectConfig(str(project_conf))
    assert config.get("platformio", "name") == "custom-project-name"


def test_nested_interpolation(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[platformio]
build_dir = /tmp/pio-$PROJECT_HASH
data_dir = $PROJECT_DIR/assets

[env:myenv]
build_flags =
    -D UTIME=${UNIX_TIME}
    -I ${PROJECTSRC_DIR}/hal
    -Wl,-Map,${BUILD_DIR}/${PROGNAME}.map
test_testing_command =
    ${platformio.packages_dir}/tool-simavr/bin/simavr
     -m
     atmega328p
     -f
     16000000L
     ${UPLOAD_PORT and "-p "+UPLOAD_PORT}
     ${platformio.build_dir}/${this.__env__}/firmware.elf
    """
    )
    config = ProjectConfig(str(project_conf))
    assert config.get("platformio", "data_dir").endswith(
        os.path.join("$PROJECT_DIR", "assets")
    )
    assert config.get("env:myenv", "build_flags")[0][-10:].isdigit()
    assert config.get("env:myenv", "build_flags")[1] == "-I ${PROJECTSRC_DIR}/hal"
    assert (
        config.get("env:myenv", "build_flags")[2]
        == "-Wl,-Map,${BUILD_DIR}/${PROGNAME}.map"
    )
    testing_command = config.get("env:myenv", "test_testing_command")
    assert "$" not in testing_command[0]
    assert testing_command[5] == '${UPLOAD_PORT and "-p "+UPLOAD_PORT}'


def test_extends_order(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[a]
board = test

[b]
upload_tool = two

[c]
upload_tool = three

[env:na_ti-ve13]
extends = a, b, c
    """
    )
    config = ProjectConfig(str(project_conf))
    assert config.get("env:na_ti-ve13", "upload_tool") == "three"


def test_invalid_env_names(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[env:app:1]
    """
    )
    config = ProjectConfig(str(project_conf))
    with pytest.raises(InvalidEnvNameError, match=r".*Invalid environment name 'app:1"):
        config.validate()


def test_linting_errors(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[env:app1]
lib_use = 1
broken_line
    """
    )
    result = ProjectConfig.lint(str(project_conf))
    assert not result["warnings"]
    assert result["errors"] and len(result["errors"]) == 1
    error = result["errors"][0]
    assert error["type"] == "ParsingError"
    assert error["lineno"] == 4


def test_linting_warnings(tmp_path: Path):
    project_conf = tmp_path / "platformio.ini"
    project_conf.write_text(
        """
[platformio]
build_dir = /tmp/pio-$PROJECT_HASH

[env:app1]
lib_use = 1
test_testing_command = /usr/bin/flash-tool -p $UPLOAD_PORT -b $UPLOAD_SPEED
    """
    )
    result = ProjectConfig.lint(str(project_conf))
    assert not result["errors"]
    assert result["warnings"] and len(result["warnings"]) == 2
    assert "deprecated" in result["warnings"][0]
    assert "Invalid variable declaration" in result["warnings"][1]
