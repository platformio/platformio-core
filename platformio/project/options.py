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

from collections import OrderedDict, namedtuple

import click

ConfigOptionClass = namedtuple("ConfigOption", [
    "scope", "name", "type", "multiple", "sysenvvar", "buildenvvar", "oldnames"
])


def ConfigOption(scope,
                 name,
                 type=str,
                 multiple=False,
                 sysenvvar=None,
                 buildenvvar=None,
                 oldnames=None):
    return ConfigOptionClass(scope, name, type, multiple, sysenvvar,
                             buildenvvar, oldnames)


def ConfigPlatformioOption(*args, **kwargs):
    return ConfigOption("platformio", *args, **kwargs)


def ConfigEnvOption(*args, **kwargs):
    return ConfigOption("env", *args, **kwargs)


ProjectOptions = OrderedDict([
    ("%s.%s" % (option.scope, option.name), option) for option in [
        #
        # [platformio]
        #
        ConfigPlatformioOption(name="description"),
        ConfigPlatformioOption(name="default_envs",
                               oldnames=["env_default"],
                               multiple=True,
                               sysenvvar="PLATFORMIO_DEFAULT_ENVS"),
        ConfigPlatformioOption(name="extra_configs", multiple=True),

        # Dirs
        ConfigPlatformioOption(name="core_dir",
                               oldnames=["home_dir"],
                               sysenvvar="PLATFORMIO_CORE_DIR"),
        ConfigPlatformioOption(name="globallib_dir",
                               sysenvvar="PLATFORMIO_GLOBALLIB_DIR"),
        ConfigPlatformioOption(name="platforms_dir",
                               sysenvvar="PLATFORMIO_PLATFORMS_DIR"),
        ConfigPlatformioOption(name="packages_dir",
                               sysenvvar="PLATFORMIO_PACKAGES_DIR"),
        ConfigPlatformioOption(name="cache_dir",
                               sysenvvar="PLATFORMIO_CACHE_DIR"),
        ConfigPlatformioOption(name="build_cache_dir",
                               sysenvvar="PLATFORMIO_BUILD_CACHE_DIR"),
        ConfigPlatformioOption(name="workspace_dir",
                               sysenvvar="PLATFORMIO_WORKSPACE_DIR"),
        ConfigPlatformioOption(name="build_dir",
                               sysenvvar="PLATFORMIO_BUILD_DIR"),
        ConfigPlatformioOption(name="libdeps_dir",
                               sysenvvar="PLATFORMIO_LIBDEPS_DIR"),
        ConfigPlatformioOption(name="lib_dir", sysenvvar="PLATFORMIO_LIB_DIR"),
        ConfigPlatformioOption(name="include_dir",
                               sysenvvar="PLATFORMIO_INCLUDE_DIR"),
        ConfigPlatformioOption(name="src_dir", sysenvvar="PLATFORMIO_SRC_DIR"),
        ConfigPlatformioOption(name="test_dir",
                               sysenvvar="PLATFORMIO_TEST_DIR"),
        ConfigPlatformioOption(name="boards_dir",
                               sysenvvar="PLATFORMIO_BOARDS_DIR"),
        ConfigPlatformioOption(name="data_dir",
                               sysenvvar="PLATFORMIO_DATA_DIR"),
        ConfigPlatformioOption(name="shared_dir",
                               sysenvvar="PLATFORMIO_SHARED_DIR"),

        #
        # [env]
        #

        # Generic
        ConfigEnvOption(name="platform", buildenvvar="PIOPLATFORM"),
        ConfigEnvOption(name="platform_packages", multiple=True),
        ConfigEnvOption(
            name="framework", multiple=True, buildenvvar="PIOFRAMEWORK"),

        # Board
        ConfigEnvOption(name="board", buildenvvar="BOARD"),
        ConfigEnvOption(name="board_build.mcu",
                        oldnames=["board_mcu"],
                        buildenvvar="BOARD_MCU"),
        ConfigEnvOption(name="board_build.f_cpu",
                        oldnames=["board_f_cpu"],
                        buildenvvar="BOARD_F_CPU"),
        ConfigEnvOption(name="board_build.f_flash",
                        oldnames=["board_f_flash"],
                        buildenvvar="BOARD_F_FLASH"),
        ConfigEnvOption(name="board_build.flash_mode",
                        oldnames=["board_flash_mode"],
                        buildenvvar="BOARD_FLASH_MODE"),

        # Build
        ConfigEnvOption(name="build_type",
                        type=click.Choice(["release", "debug"])),
        ConfigEnvOption(name="build_flags",
                        multiple=True,
                        sysenvvar="PLATFORMIO_BUILD_FLAGS",
                        buildenvvar="BUILD_FLAGS"),
        ConfigEnvOption(name="src_build_flags",
                        multiple=True,
                        sysenvvar="PLATFORMIO_SRC_BUILD_FLAGS",
                        buildenvvar="SRC_BUILD_FLAGS"),
        ConfigEnvOption(name="build_unflags",
                        multiple=True,
                        sysenvvar="PLATFORMIO_BUILD_UNFLAGS",
                        buildenvvar="BUILD_UNFLAGS"),
        ConfigEnvOption(name="src_filter",
                        multiple=True,
                        sysenvvar="PLATFORMIO_SRC_FILTER",
                        buildenvvar="SRC_FILTER"),
        ConfigEnvOption(name="targets", multiple=True),

        # Upload
        ConfigEnvOption(name="upload_port",
                        sysenvvar="PLATFORMIO_UPLOAD_PORT",
                        buildenvvar="UPLOAD_PORT"),
        ConfigEnvOption(name="upload_protocol", buildenvvar="UPLOAD_PROTOCOL"),
        ConfigEnvOption(
            name="upload_speed", type=click.INT, buildenvvar="UPLOAD_SPEED"),
        ConfigEnvOption(name="upload_flags",
                        multiple=True,
                        sysenvvar="PLATFORMIO_UPLOAD_FLAGS",
                        buildenvvar="UPLOAD_FLAGS"),
        ConfigEnvOption(name="upload_resetmethod",
                        buildenvvar="UPLOAD_RESETMETHOD"),
        ConfigEnvOption(name="upload_command", buildenvvar="UPLOADCMD"),

        # Monitor
        ConfigEnvOption(name="monitor_port"),
        ConfigEnvOption(name="monitor_speed", oldnames=["monitor_baud"]),
        ConfigEnvOption(name="monitor_rts", type=click.IntRange(0, 1)),
        ConfigEnvOption(name="monitor_dtr", type=click.IntRange(0, 1)),
        ConfigEnvOption(name="monitor_flags", multiple=True),

        # Library
        ConfigEnvOption(name="lib_deps",
                        oldnames=["lib_use", "lib_force", "lib_install"],
                        multiple=True),
        ConfigEnvOption(name="lib_ignore", multiple=True),
        ConfigEnvOption(name="lib_extra_dirs",
                        multiple=True,
                        sysenvvar="PLATFORMIO_LIB_EXTRA_DIRS"),
        ConfigEnvOption(name="lib_ldf_mode",
                        type=click.Choice(
                            ["off", "chain", "deep", "chain+", "deep+"])),
        ConfigEnvOption(name="lib_compat_mode",
                        type=click.Choice(["off", "soft", "strict"])),
        ConfigEnvOption(name="lib_archive", type=click.BOOL),

        # Test
        ConfigEnvOption(name="test_filter", multiple=True),
        ConfigEnvOption(name="test_ignore", multiple=True),
        ConfigEnvOption(name="test_port"),
        ConfigEnvOption(name="test_speed", type=click.INT),
        ConfigEnvOption(name="test_transport"),
        ConfigEnvOption(name="test_build_project_src", type=click.BOOL),

        # Debug
        ConfigEnvOption(name="debug_tool"),
        ConfigEnvOption(name="debug_init_break"),
        ConfigEnvOption(name="debug_init_cmds", multiple=True),
        ConfigEnvOption(name="debug_extra_cmds", multiple=True),
        ConfigEnvOption(name="debug_load_cmds",
                        oldnames=["debug_load_cmd"],
                        multiple=True),
        ConfigEnvOption(name="debug_load_mode",
                        type=click.Choice(["always", "modified", "manual"])),
        ConfigEnvOption(name="debug_server", multiple=True),
        ConfigEnvOption(name="debug_port"),
        ConfigEnvOption(name="debug_svd_path",
                        type=click.Path(
                            exists=True, file_okay=True, dir_okay=False)),

        # Other
        ConfigEnvOption(name="extra_scripts",
                        oldnames=["extra_script"],
                        multiple=True,
                        sysenvvar="PLATFORMIO_EXTRA_SCRIPTS")
    ]
])
