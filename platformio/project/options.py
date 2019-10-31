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

# pylint: disable=redefined-builtin, too-many-arguments

import os
from collections import OrderedDict

import click

from platformio import fs


class ConfigOption(object):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        scope,
        group,
        name,
        type=str,
        multiple=False,
        sysenvvar=None,
        buildenvvar=None,
        oldnames=None,
        default=None,
        description=None,
    ):
        self.scope = scope
        self.group = group
        self.name = name
        self.type = type
        self.multiple = multiple
        self.sysenvvar = sysenvvar
        self.buildenvvar = buildenvvar
        self.oldnames = oldnames
        self.default = default
        self.description = description

    def as_dict(self):
        result = dict(
            scope=self.scope,
            group=self.group,
            name=self.name,
            type="string",
            multiple=self.multiple,
            default=self.default,
            description=self.description,
        )
        if isinstance(self.type, click.ParamType):
            result["type"] = self.type.name

        if isinstance(self.type, (click.IntRange, click.FloatRange)):
            result["min"] = self.type.min
            result["max"] = self.type.max
        if isinstance(self.type, click.Choice):
            result["choices"] = self.type.choices

        return result


def ConfigPlatformioOption(*args, **kwargs):
    return ConfigOption("platformio", *args, **kwargs)


def ConfigEnvOption(*args, **kwargs):
    return ConfigOption("env", *args, **kwargs)


ProjectOptions = OrderedDict(
    [
        ("%s.%s" % (option.scope, option.name), option)
        for option in [
            #
            # [platformio]
            #
            ConfigPlatformioOption(group="generic", name="description"),
            ConfigPlatformioOption(
                group="generic",
                name="default_envs",
                oldnames=["env_default"],
                multiple=True,
                sysenvvar="PLATFORMIO_DEFAULT_ENVS",
            ),
            ConfigPlatformioOption(
                group="generic", name="extra_configs", multiple=True
            ),
            # Dirs
            ConfigPlatformioOption(
                group="directory",
                name="core_dir",
                oldnames=["home_dir"],
                sysenvvar="PLATFORMIO_CORE_DIR",
                default=os.path.join(fs.expanduser("~"), ".platformio"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="globallib_dir",
                sysenvvar="PLATFORMIO_GLOBALLIB_DIR",
                default=os.path.join("$PROJECT_CORE_DIR", "lib"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="platforms_dir",
                sysenvvar="PLATFORMIO_PLATFORMS_DIR",
                default=os.path.join("$PROJECT_CORE_DIR", "platforms"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="packages_dir",
                sysenvvar="PLATFORMIO_PACKAGES_DIR",
                default=os.path.join("$PROJECT_CORE_DIR", "packages"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="cache_dir",
                sysenvvar="PLATFORMIO_CACHE_DIR",
                default=os.path.join("$PROJECT_CORE_DIR", ".cache"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="build_cache_dir",
                sysenvvar="PLATFORMIO_BUILD_CACHE_DIR",
            ),
            ConfigPlatformioOption(
                group="directory",
                name="workspace_dir",
                sysenvvar="PLATFORMIO_WORKSPACE_DIR",
                default=os.path.join("$PROJECT_DIR", ".pio"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="build_dir",
                sysenvvar="PLATFORMIO_BUILD_DIR",
                default=os.path.join("$PROJECT_WORKSPACE_DIR", "build"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="libdeps_dir",
                sysenvvar="PLATFORMIO_LIBDEPS_DIR",
                default=os.path.join("$PROJECT_WORKSPACE_DIR", "libdeps"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="lib_dir",
                sysenvvar="PLATFORMIO_LIB_DIR",
                default=os.path.join("$PROJECT_DIR", "lib"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="include_dir",
                sysenvvar="PLATFORMIO_INCLUDE_DIR",
                default=os.path.join("$PROJECT_DIR", "include"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="src_dir",
                sysenvvar="PLATFORMIO_SRC_DIR",
                default=os.path.join("$PROJECT_DIR", "src"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="test_dir",
                sysenvvar="PLATFORMIO_TEST_DIR",
                default=os.path.join("$PROJECT_DIR", "test"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="boards_dir",
                sysenvvar="PLATFORMIO_BOARDS_DIR",
                default=os.path.join("$PROJECT_DIR", "boards"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="data_dir",
                sysenvvar="PLATFORMIO_DATA_DIR",
                default=os.path.join("$PROJECT_DIR", "data"),
            ),
            ConfigPlatformioOption(
                group="directory",
                name="shared_dir",
                sysenvvar="PLATFORMIO_SHARED_DIR",
                default=os.path.join("$PROJECT_DIR", "shared"),
            ),
            #
            # [env]
            #
            # Platform
            ConfigEnvOption(
                group="platform", name="platform", buildenvvar="PIOPLATFORM"
            ),
            ConfigEnvOption(group="platform", name="platform_packages", multiple=True),
            ConfigEnvOption(
                group="platform",
                name="framework",
                multiple=True,
                buildenvvar="PIOFRAMEWORK",
            ),
            # Board
            ConfigEnvOption(group="board", name="board", buildenvvar="BOARD"),
            ConfigEnvOption(
                group="board",
                name="board_build.mcu",
                oldnames=["board_mcu"],
                buildenvvar="BOARD_MCU",
            ),
            ConfigEnvOption(
                group="board",
                name="board_build.f_cpu",
                oldnames=["board_f_cpu"],
                buildenvvar="BOARD_F_CPU",
            ),
            ConfigEnvOption(
                group="board",
                name="board_build.f_flash",
                oldnames=["board_f_flash"],
                buildenvvar="BOARD_F_FLASH",
            ),
            ConfigEnvOption(
                group="board",
                name="board_build.flash_mode",
                oldnames=["board_flash_mode"],
                buildenvvar="BOARD_FLASH_MODE",
            ),
            # Build
            ConfigEnvOption(
                group="build",
                name="build_type",
                type=click.Choice(["release", "debug"]),
            ),
            ConfigEnvOption(
                group="build",
                name="build_flags",
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_FLAGS",
                buildenvvar="BUILD_FLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="src_build_flags",
                multiple=True,
                sysenvvar="PLATFORMIO_SRC_BUILD_FLAGS",
                buildenvvar="SRC_BUILD_FLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="build_unflags",
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_UNFLAGS",
                buildenvvar="BUILD_UNFLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="src_filter",
                multiple=True,
                sysenvvar="PLATFORMIO_SRC_FILTER",
                buildenvvar="SRC_FILTER",
            ),
            ConfigEnvOption(group="build", name="targets", multiple=True),
            # Upload
            ConfigEnvOption(
                group="upload",
                name="upload_port",
                sysenvvar="PLATFORMIO_UPLOAD_PORT",
                buildenvvar="UPLOAD_PORT",
            ),
            ConfigEnvOption(
                group="upload", name="upload_protocol", buildenvvar="UPLOAD_PROTOCOL"
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_speed",
                type=click.INT,
                buildenvvar="UPLOAD_SPEED",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_flags",
                multiple=True,
                sysenvvar="PLATFORMIO_UPLOAD_FLAGS",
                buildenvvar="UPLOAD_FLAGS",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_resetmethod",
                buildenvvar="UPLOAD_RESETMETHOD",
            ),
            ConfigEnvOption(
                group="upload", name="upload_command", buildenvvar="UPLOADCMD"
            ),
            # Monitor
            ConfigEnvOption(group="monitor", name="monitor_port"),
            ConfigEnvOption(
                group="monitor", name="monitor_speed", oldnames=["monitor_baud"]
            ),
            ConfigEnvOption(
                group="monitor", name="monitor_rts", type=click.IntRange(0, 1)
            ),
            ConfigEnvOption(
                group="monitor", name="monitor_dtr", type=click.IntRange(0, 1)
            ),
            ConfigEnvOption(group="monitor", name="monitor_flags", multiple=True),
            # Library
            ConfigEnvOption(
                group="lib",
                name="lib_deps",
                oldnames=["lib_use", "lib_force", "lib_install"],
                multiple=True,
            ),
            ConfigEnvOption(group="lib", name="lib_ignore", multiple=True),
            ConfigEnvOption(
                group="lib",
                name="lib_extra_dirs",
                multiple=True,
                sysenvvar="PLATFORMIO_LIB_EXTRA_DIRS",
            ),
            ConfigEnvOption(
                group="lib",
                name="lib_ldf_mode",
                type=click.Choice(["off", "chain", "deep", "chain+", "deep+"]),
            ),
            ConfigEnvOption(
                group="lib",
                name="lib_compat_mode",
                type=click.Choice(["off", "soft", "strict"]),
            ),
            ConfigEnvOption(
                group="lib", name="lib_archive", type=click.BOOL, default=True
            ),
            # Test
            ConfigEnvOption(group="test", name="test_filter", multiple=True),
            ConfigEnvOption(group="test", name="test_ignore", multiple=True),
            ConfigEnvOption(group="test", name="test_port"),
            ConfigEnvOption(group="test", name="test_speed", type=click.INT),
            ConfigEnvOption(group="test", name="test_transport"),
            ConfigEnvOption(
                group="test",
                name="test_build_project_src",
                type=click.BOOL,
                default=False,
            ),
            # Debug
            ConfigEnvOption(group="debug", name="debug_tool"),
            ConfigEnvOption(group="debug", name="debug_init_break"),
            ConfigEnvOption(group="debug", name="debug_init_cmds", multiple=True),
            ConfigEnvOption(group="debug", name="debug_extra_cmds", multiple=True),
            ConfigEnvOption(
                group="debug",
                name="debug_load_cmds",
                oldnames=["debug_load_cmd"],
                multiple=True,
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_load_mode",
                type=click.Choice(["always", "modified", "manual"]),
            ),
            ConfigEnvOption(group="debug", name="debug_server", multiple=True),
            ConfigEnvOption(group="debug", name="debug_port"),
            ConfigEnvOption(
                group="debug",
                name="debug_svd_path",
                type=click.Path(exists=True, file_okay=True, dir_okay=False),
            ),
            # Check
            ConfigEnvOption(group="check", name="check_tool", multiple=True),
            ConfigEnvOption(group="check", name="check_filter", multiple=True),
            ConfigEnvOption(group="check", name="check_flags", multiple=True),
            ConfigEnvOption(
                group="check",
                name="check_severity",
                multiple=True,
                type=click.Choice(["low", "medium", "high"]),
            ),
            # Advanced
            ConfigEnvOption(
                group="advanced",
                name="extra_scripts",
                oldnames=["extra_script"],
                multiple=True,
                sysenvvar="PLATFORMIO_EXTRA_SCRIPTS",
            ),
            ConfigEnvOption(group="advanced", name="extends", multiple=True),
        ]
    ]
)


def get_config_options_schema():
    return [option.as_dict() for option in ProjectOptions.values()]
