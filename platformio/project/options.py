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
from platformio.compat import IS_WINDOWS


class ConfigOption:  # pylint: disable=too-many-instance-attributes,too-many-positional-arguments
    def __init__(
        self,
        scope,
        group,
        name,
        description,
        type=str,
        multiple=False,
        sysenvvar=None,
        buildenvvar=None,
        oldnames=None,
        default=None,
        validate=None,
    ):
        self.scope = scope
        self.group = group
        self.name = name
        self.description = description
        self.type = type
        self.multiple = multiple
        self.sysenvvar = sysenvvar
        self.buildenvvar = buildenvvar
        self.oldnames = oldnames
        self.default = default
        self.validate = validate

    def as_dict(self):
        result = dict(
            scope=self.scope,
            group=self.group,
            name=self.name,
            description=self.description,
            type="string",
            multiple=self.multiple,
            sysenvvar=self.sysenvvar,
            default=self.default() if callable(self.default) else self.default,
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


def validate_dir(path):
    if not path:
        return path
    # if not all values expanded, ignore validation
    if "${" in path and "}" in path:
        return path
    if path.startswith("~"):
        path = fs.expanduser(path)
    return os.path.abspath(path)


def get_default_core_dir():
    path = os.path.join(fs.expanduser("~"), ".platformio")
    if IS_WINDOWS:
        win_core_dir = os.path.splitdrive(path)[0] + "\\.platformio"
        if os.path.isdir(win_core_dir):
            return win_core_dir
    return path


ProjectOptions = OrderedDict(
    [
        ("%s.%s" % (option.scope, option.name), option)
        for option in [
            #
            # [platformio]
            #
            ConfigPlatformioOption(
                group="generic",
                name="name",
                description="A project name",
                default=lambda: os.path.basename(os.getcwd()),
            ),
            ConfigPlatformioOption(
                group="generic",
                name="description",
                description="Describe a project with a short information",
            ),
            ConfigPlatformioOption(
                group="generic",
                name="default_envs",
                description=(
                    "Configure a list with environments which PlatformIO should "
                    "process by default"
                ),
                oldnames=["env_default"],
                multiple=True,
                sysenvvar="PLATFORMIO_DEFAULT_ENVS",
            ),
            ConfigPlatformioOption(
                group="generic",
                name="extra_configs",
                description=(
                    "Extend main configuration with the extra configuration files"
                ),
                multiple=True,
            ),
            # Dirs
            ConfigPlatformioOption(
                group="directory",
                name="core_dir",
                description=(
                    "PlatformIO Core location where it keeps installed development "
                    "platforms, packages, global libraries, "
                    "and other internal information"
                ),
                oldnames=["home_dir"],
                sysenvvar="PLATFORMIO_CORE_DIR",
                default=get_default_core_dir,
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="globallib_dir",
                description=(
                    "A library folder/storage where PlatformIO Library Dependency "
                    "Finder (LDF) looks for global libraries"
                ),
                sysenvvar="PLATFORMIO_GLOBALLIB_DIR",
                default=os.path.join("${platformio.core_dir}", "lib"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="platforms_dir",
                description=(
                    "A location where PlatformIO Core keeps installed development "
                    "platforms"
                ),
                sysenvvar="PLATFORMIO_PLATFORMS_DIR",
                default=os.path.join("${platformio.core_dir}", "platforms"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="packages_dir",
                description=(
                    "A location where PlatformIO Core keeps installed packages"
                ),
                sysenvvar="PLATFORMIO_PACKAGES_DIR",
                default=os.path.join("${platformio.core_dir}", "packages"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="cache_dir",
                description=(
                    "A location where PlatformIO Core stores caching information "
                    "(requests to PlatformIO Registry, downloaded packages and "
                    "other service information)"
                ),
                sysenvvar="PLATFORMIO_CACHE_DIR",
                default=os.path.join("${platformio.core_dir}", ".cache"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="build_cache_dir",
                description=(
                    "A location where PlatformIO Core keeps derived files from a "
                    "build system (objects, firmwares, ELFs) and caches them between "
                    "build environments"
                ),
                sysenvvar="PLATFORMIO_BUILD_CACHE_DIR",
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="workspace_dir",
                description=(
                    "A path to a project workspace directory where PlatformIO keeps "
                    "by default compiled objects, static libraries, firmwares, and "
                    "external library dependencies"
                ),
                sysenvvar="PLATFORMIO_WORKSPACE_DIR",
                default=os.path.join("${PROJECT_DIR}", ".pio"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="build_dir",
                description=(
                    "PlatformIO Build System uses this folder for project environments"
                    " to store compiled object files, static libraries, firmwares, "
                    "and other cached information"
                ),
                sysenvvar="PLATFORMIO_BUILD_DIR",
                default=os.path.join("${platformio.workspace_dir}", "build"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="libdeps_dir",
                description=(
                    "Internal storage where Library Manager will install project "
                    "dependencies declared via `lib_deps` option"
                ),
                sysenvvar="PLATFORMIO_LIBDEPS_DIR",
                default=os.path.join("${platformio.workspace_dir}", "libdeps"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="include_dir",
                description=(
                    "A default location for project header files. PlatformIO Build "
                    "System automatically adds this path to CPPPATH scope"
                ),
                sysenvvar="PLATFORMIO_INCLUDE_DIR",
                default=os.path.join("${PROJECT_DIR}", "include"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="src_dir",
                description=(
                    "A default location where PlatformIO Build System looks for the "
                    "project C/C++ source files"
                ),
                sysenvvar="PLATFORMIO_SRC_DIR",
                default=os.path.join("${PROJECT_DIR}", "src"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="lib_dir",
                description="A storage for the custom/private project libraries",
                sysenvvar="PLATFORMIO_LIB_DIR",
                default=os.path.join("${PROJECT_DIR}", "lib"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="data_dir",
                description=(
                    "A data directory to store contents which can be uploaded to "
                    "file system (SPIFFS, etc.)"
                ),
                sysenvvar="PLATFORMIO_DATA_DIR",
                default=os.path.join("${PROJECT_DIR}", "data"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="test_dir",
                description=(
                    "A location where PlatformIO Unit Testing engine looks for "
                    "test source files"
                ),
                sysenvvar="PLATFORMIO_TEST_DIR",
                default=os.path.join("${PROJECT_DIR}", "test"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="boards_dir",
                description="A storage for custom board manifests",
                sysenvvar="PLATFORMIO_BOARDS_DIR",
                default=os.path.join("${PROJECT_DIR}", "boards"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="monitor_dir",
                description="A storage for custom monitor filters",
                sysenvvar="PLATFORMIO_MONITOR_DIR",
                default=os.path.join("${PROJECT_DIR}", "monitor"),
                validate=validate_dir,
            ),
            ConfigPlatformioOption(
                group="directory",
                name="shared_dir",
                description=(
                    "A location which PlatformIO Remote Development service uses to "
                    "synchronize extra files between remote machines"
                ),
                sysenvvar="PLATFORMIO_SHARED_DIR",
                default=os.path.join("${PROJECT_DIR}", "shared"),
                validate=validate_dir,
            ),
            #
            # [env]
            #
            # Platform
            ConfigEnvOption(
                group="platform",
                name="platform",
                description="A name or specification of development platform",
                buildenvvar="PIOPLATFORM",
            ),
            ConfigEnvOption(
                group="platform",
                name="platform_packages",
                description="Custom packages and specifications",
                multiple=True,
            ),
            # Board
            ConfigEnvOption(
                group="platform",
                name="board",
                description="A board ID",
                buildenvvar="BOARD",
            ),
            ConfigEnvOption(
                group="platform",
                name="framework",
                description="A list of project dependent frameworks",
                multiple=True,
                buildenvvar="PIOFRAMEWORK",
            ),
            ConfigEnvOption(
                group="platform",
                name="board_build.mcu",
                description="A custom board MCU",
                oldnames=["board_mcu"],
                buildenvvar="BOARD_MCU",
            ),
            ConfigEnvOption(
                group="platform",
                name="board_build.f_cpu",
                description="A custom MCU frequency",
                oldnames=["board_f_cpu"],
                buildenvvar="BOARD_F_CPU",
            ),
            ConfigEnvOption(
                group="platform",
                name="board_build.f_flash",
                description="A custom flash frequency",
                oldnames=["board_f_flash"],
                buildenvvar="BOARD_F_FLASH",
            ),
            ConfigEnvOption(
                group="platform",
                name="board_build.flash_mode",
                description="A custom flash mode",
                oldnames=["board_flash_mode"],
                buildenvvar="BOARD_FLASH_MODE",
            ),
            # Build
            ConfigEnvOption(
                group="build",
                name="build_type",
                description="Project build configuration",
                type=click.Choice(["release", "test", "debug"]),
                default="release",
            ),
            ConfigEnvOption(
                group="build",
                name="build_flags",
                description=(
                    "Custom build flags/options for preprocessing, compilation, "
                    "assembly, and linking processes"
                ),
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_FLAGS",
                buildenvvar="BUILD_FLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="build_src_flags",
                oldnames=["src_build_flags"],
                description=(
                    "The same as `build_flags` but configures flags the only for "
                    "project source files in the `src` folder"
                ),
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_SRC_FLAGS",
                buildenvvar="SRC_BUILD_FLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="build_unflags",
                description="A list with flags/option which should be removed",
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_UNFLAGS",
                buildenvvar="BUILD_UNFLAGS",
            ),
            ConfigEnvOption(
                group="build",
                name="build_src_filter",
                oldnames=["src_filter"],
                description=(
                    "Control which source files from the `src` folder should "
                    "be included/excluded from a build process"
                ),
                multiple=True,
                sysenvvar="PLATFORMIO_BUILD_SRC_FILTER",
                buildenvvar="SRC_FILTER",
                default="+<*> -<.git/> -<.svn/>",
            ),
            ConfigEnvOption(
                group="build",
                name="targets",
                description="A custom list of targets for PlatformIO Build System",
                multiple=True,
            ),
            # Upload
            ConfigEnvOption(
                group="upload",
                name="upload_port",
                description=(
                    "An upload port which `uploader` tool uses for a firmware flashing"
                ),
                sysenvvar="PLATFORMIO_UPLOAD_PORT",
                buildenvvar="UPLOAD_PORT",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_protocol",
                description="A protocol that `uploader` tool uses to talk to a board",
                buildenvvar="UPLOAD_PROTOCOL",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_speed",
                description=(
                    "A connection speed (baud rate) which `uploader` tool uses when "
                    "sending firmware to a board"
                ),
                type=click.INT,
                buildenvvar="UPLOAD_SPEED",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_flags",
                description="An extra flags for `uploader` tool",
                multiple=True,
                sysenvvar="PLATFORMIO_UPLOAD_FLAGS",
                buildenvvar="UPLOAD_FLAGS",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_resetmethod",
                description="A custom reset method",
                buildenvvar="UPLOAD_RESETMETHOD",
            ),
            ConfigEnvOption(
                group="upload",
                name="upload_command",
                description=(
                    "A custom upload command which overwrites a default from "
                    "development platform"
                ),
                buildenvvar="UPLOADCMD",
            ),
            # Monitor
            ConfigEnvOption(
                group="monitor",
                name="monitor_port",
                description="A port, a number or a device name",
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_speed",
                description="A monitor speed (baud rate)",
                type=click.INT,
                oldnames=["monitor_baud"],
                default=9600,
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_parity",
                description="A monitor parity checking",
                type=click.Choice(["N", "E", "O", "S", "M"]),
                default="N",
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_filters",
                description=(
                    "Apply the filters and text transformations to monitor output"
                ),
                multiple=True,
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_rts",
                description="A monitor initial RTS line state",
                type=click.IntRange(0, 1),
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_dtr",
                description="A monitor initial DTR line state",
                type=click.IntRange(0, 1),
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_eol",
                description="A monitor end of line mode",
                type=click.Choice(["CR", "LF", "CRLF"]),
                default="CRLF",
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_raw",
                description="Disable encodings/transformations of device output",
                type=click.BOOL,
                default=False,
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_echo",
                description="Enable a monitor local echo",
                type=click.BOOL,
                default=False,
            ),
            ConfigEnvOption(
                group="monitor",
                name="monitor_encoding",
                description="Custom encoding (e.g. hexlify, Latin-1, UTF-8)",
                default="UTF-8",
            ),
            # Library
            ConfigEnvOption(
                group="library",
                name="lib_deps",
                description=(
                    "A list of project library dependencies which should be installed "
                    "automatically before a build process"
                ),
                oldnames=["lib_use", "lib_force", "lib_install"],
                multiple=True,
            ),
            ConfigEnvOption(
                group="library",
                name="lib_ignore",
                description=(
                    "A list of library names which should be ignored by "
                    "Library Dependency Finder (LDF)"
                ),
                multiple=True,
            ),
            ConfigEnvOption(
                group="library",
                name="lib_extra_dirs",
                description=(
                    "A list of extra directories/storages where Library Dependency "
                    "Finder (LDF) will look for dependencies"
                ),
                multiple=True,
                sysenvvar="PLATFORMIO_LIB_EXTRA_DIRS",
            ),
            ConfigEnvOption(
                group="library",
                name="lib_ldf_mode",
                description=(
                    "Control how Library Dependency Finder (LDF) should analyze "
                    "dependencies (`#include` directives)"
                ),
                type=click.Choice(["off", "chain", "deep", "chain+", "deep+"]),
                default="chain",
            ),
            ConfigEnvOption(
                group="library",
                name="lib_compat_mode",
                description=(
                    "Configure a strictness (compatibility mode by frameworks, "
                    "development platforms) of Library Dependency Finder (LDF)"
                ),
                type=click.Choice(["off", "soft", "strict"]),
                default="soft",
            ),
            ConfigEnvOption(
                group="library",
                name="lib_archive",
                description=(
                    "Create an archive (`*.a`, static library) from the object files "
                    "and link it into a firmware (program)"
                ),
                type=click.BOOL,
                default=True,
            ),
            # Check
            ConfigEnvOption(
                group="check",
                name="check_tool",
                description="A list of check tools used for analysis",
                type=click.Choice(["cppcheck", "clangtidy", "pvs-studio"]),
                multiple=True,
                default=["cppcheck"],
            ),
            ConfigEnvOption(
                group="check",
                name="check_src_filters",
                oldnames=["check_patterns"],
                description=(
                    "Configure a list of target files or directories for checking"
                ),
                multiple=True,
            ),
            ConfigEnvOption(
                group="check",
                name="check_flags",
                description="An extra flags to be passed to a check tool",
                multiple=True,
            ),
            ConfigEnvOption(
                group="check",
                name="check_severity",
                description="List of defect severity types for analysis",
                multiple=True,
                type=click.Choice(["low", "medium", "high"]),
                default=["low", "medium", "high"],
            ),
            ConfigEnvOption(
                group="check",
                name="check_skip_packages",
                description="Skip checking includes from packages directory",
                type=click.BOOL,
                default=False,
            ),
            # Test
            ConfigEnvOption(
                group="test",
                name="test_framework",
                description="A unit testing framework",
                type=click.Choice(["doctest", "googletest", "unity", "custom"]),
                default="unity",
            ),
            ConfigEnvOption(
                group="test",
                name="test_filter",
                description="Process tests where the name matches specified patterns",
                multiple=True,
            ),
            ConfigEnvOption(
                group="test",
                name="test_ignore",
                description="Ignore tests where the name matches specified patterns",
                multiple=True,
            ),
            ConfigEnvOption(
                group="test",
                name="test_port",
                description="A serial port to communicate with a target device",
            ),
            ConfigEnvOption(
                group="test",
                name="test_speed",
                description="A connection speed (baud rate) to communicate with "
                "a target device",
                type=click.INT,
                default=115200,
            ),
            ConfigEnvOption(
                group="test",
                name="test_build_src",
                oldnames=["test_build_project_src"],
                description="Build main source code in pair with a test code",
                type=click.BOOL,
                default=False,
            ),
            ConfigEnvOption(
                group="test",
                name="test_testing_command",
                multiple=True,
                description=(
                    "A custom testing command that runs test cases "
                    "and returns results to the standard output"
                ),
            ),
            # Debug
            ConfigEnvOption(
                group="debug",
                name="debug_tool",
                description="A name of debugging tool",
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_build_flags",
                description=(
                    "Custom debug flags/options for preprocessing, compilation, "
                    "assembly, and linking processes"
                ),
                multiple=True,
                default=["-Og", "-g2", "-ggdb2"],
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_init_break",
                description=(
                    "An initial breakpoint that makes program stop whenever a "
                    "certain point in the program is reached"
                ),
                default="tbreak main",
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_init_cmds",
                description="Initial commands to be passed to a back-end debugger",
                multiple=True,
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_extra_cmds",
                description="An extra commands to be passed to a back-end debugger",
                multiple=True,
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_load_cmds",
                description=(
                    "A list of commands to be used to load program/firmware "
                    "to a target device"
                ),
                oldnames=["debug_load_cmd"],
                multiple=True,
                default=["load"],
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_load_mode",
                description=(
                    "Allows one to control when PlatformIO should load debugging "
                    "firmware to the end target"
                ),
                type=click.Choice(["always", "modified", "manual"]),
                default="always",
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_server",
                description="Allows one to setup a custom debugging server",
                multiple=True,
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_port",
                description=(
                    "A debugging port of a remote target (a serial device or "
                    "network address)"
                ),
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_speed",
                description="A debug adapter speed (JTAG speed)",
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_svd_path",
                description=(
                    "A custom path to SVD file which contains information about "
                    "device peripherals"
                ),
                type=click.Path(exists=True, file_okay=True, dir_okay=False),
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_server_ready_pattern",
                description=(
                    "A pattern to determine when debugging server is ready "
                    "for an incoming connection"
                ),
            ),
            ConfigEnvOption(
                group="debug",
                name="debug_test",
                description=("A name of a unit test to be debugged"),
            ),
            # Advanced
            ConfigEnvOption(
                group="advanced",
                name="extends",
                description=(
                    "Inherit configuration from other sections or build environments"
                ),
                multiple=True,
            ),
            ConfigEnvOption(
                group="advanced",
                name="extra_scripts",
                description="A list of PRE and POST extra scripts",
                oldnames=["extra_script"],
                multiple=True,
                sysenvvar="PLATFORMIO_EXTRA_SCRIPTS",
            ),
        ]
    ]
)


def get_config_options_schema():
    return [opt.as_dict() for opt in ProjectOptions.values()]
