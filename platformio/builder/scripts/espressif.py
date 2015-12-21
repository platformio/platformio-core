# Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
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

"""
    Builder for Espressif MCUs
"""

import re
import socket
from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()


def _get_flash_size(env):  # pylint: disable=redefined-outer-name
    # use board's flash size by default
    board_max_size = int(
        env.get("BOARD_OPTIONS", {}).get("upload", {}).get("maximum_size", 0))

    # check if user overrides
    for f in env.get("LINKFLAGS", []):
        if "-Wl,-T" not in f:
            continue
        match = re.search(r"-Wl,-T.*\.flash\.(\d+)(m|k).*\.ld", env.subst(f))
        if not match:
            continue
        if match.group(2) == "k":
            board_max_size = int(match.group(1)) * 1024
        elif match.group(2) == "m":
            board_max_size = int(match.group(1)) * 1024 * 1024

    return ("%dK" % (board_max_size / 1024) if board_max_size < 1048576
            else "%dM" % (board_max_size / 1048576))


env = DefaultEnvironment()

env.Replace(
    __get_flash_size=_get_flash_size,

    AR="xtensa-lx106-elf-ar",
    AS="xtensa-lx106-elf-as",
    CC="xtensa-lx106-elf-gcc",
    CXX="xtensa-lx106-elf-g++",
    OBJCOPY="xtensa-lx106-elf-objcopy",
    RANLIB="xtensa-lx106-elf-ranlib",
    SIZETOOL="xtensa-lx106-elf-size",

    ARFLAGS=["rcs"],

    ASPPFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=gnu99",
        "-Wpointer-arith",
        "-Wno-implicit-function-declaration",
        "-Wl,-EL",
        "-fno-inline-functions",
        "-nostdlib"
    ],

    CPPFLAGS=[
        "-Os",  # optimize for size
        "-mlongcalls",
        "-mtext-section-literals",
        "-falign-functions=4",
        "-U__STRICT_ANSI__",
        "-ffunction-sections",
        "-fdata-sections",
        "-MMD"  # output dependancy info
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=c++11"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU",
        "__ets__",
        "ICACHE_FLASH"
    ],

    LINKFLAGS=[
        "-nostdlib",
        "-Wl,--no-check-sections",
        "-u", "call_user_start",
        "-Wl,-static",
        "-Wl,--gc-sections"
    ],

    SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-esptool", "esptool"),
    UPLOADERFLAGS=[
        "-vv",
        "-cd", "${BOARD_OPTIONS['upload']['resetmethod']}",
        "-cb", "$UPLOAD_SPEED",
        "-cp", "$UPLOAD_PORT",
        "-cf", "$SOURCE"
    ],
    UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',

    PROGNAME="firmware",
    PROGSUFFIX=".elf"
)

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                '"$UPLOADER"',
                "-eo",
                '"%s"' % join("$PLATFORMFW_DIR", "bootloaders",
                              "eboot", "eboot.elf"),
                "-bo", "$TARGET",
                "-bm", "dio",
                "-bf", "${BOARD_OPTIONS['build']['f_cpu'][:2]}",
                "-bz", "${__get_flash_size(__env__)}",
                "-bs", ".text",
                "-bp", "4096",
                "-ec",
                "-eo", "$SOURCES",
                "-bs", ".irom0.text",
                "-bs", ".text",
                "-bs", ".data",
                "-bs", ".rodata",
                "-bc", "-ec"
            ]),
            suffix=".bin"
        )
    )
)

if "FRAMEWORK" in env:
    env.Append(
        LINKFLAGS=[
            "-Wl,-wrap,system_restart_local",
            "-Wl,-wrap,register_chipv6_phy"
        ]
    )

    # Handle uploading via OTA
    try:
        if env.get("UPLOAD_PORT") and socket.inet_aton(env.get("UPLOAD_PORT")):
            env.Replace(
                UPLOADEROTA=join("$PLATFORMFW_DIR", "tools", "espota.py"),
                UPLOADERFLAGS=[
                    "--debug",
                    "--progress",
                    "-i", "$UPLOAD_PORT",
                    "-f", "$SOURCE"
                ],
                UPLOADCMD='"$UPLOADEROTA" $UPLOADERFLAGS'
            )
    except socket.error:
        pass

# Configure native SDK
else:
    env.Append(
        CPPPATH=[
            join("$PIOPACKAGES_DIR", "sdk-esp8266", "include"),
            "$PROJECTSRC_DIR"
        ],
        LIBPATH=[join("$PIOPACKAGES_DIR", "sdk-esp8266", "lib")],
        BUILDERS=dict(
            ElfToBin=Builder(
                action=" ".join([
                    '"$UPLOADER"',
                    "-eo", "$SOURCES",
                    "-bo", "${TARGETS[0]}",
                    "-bm", "qio",
                    "-bf", "40",
                    "-bz", "512K",
                    "-bs", ".text",
                    "-bs", ".data",
                    "-bs", ".rodata",
                    "-bc", "-ec",
                    "-eo", "$SOURCES",
                    "-es", ".irom0.text", "${TARGETS[1]}",
                    "-ec", "-v"
                ]),
                suffix=".bin"
            )
        )
    )
    env.Replace(
        LDSCRIPT_PATH=join(
            "$PIOPACKAGES_DIR", "sdk-esp8266", "ld", "eagle.app.v6.ld"),
        LIBS=["c", "gcc", "phy", "pp", "net80211", "lwip", "wpa", "main",
              "json", "upgrade", "smartconfig", "pwm", "at", "ssl"],
        UPLOADERFLAGS=[
            "-vv",
            "-cd", "ck",
            "-cb", "$UPLOAD_SPEED",
            "-cp", "$UPLOAD_PORT",
            "-ca", "0x00000",
            "-cf", "${SOURCES[0]}",
            "-ca", "0x40000",
            "-cf", "${SOURCES[1]}"
        ]
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

#
# Target: Build the .hex
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    if "FRAMEWORK" not in env:
        target_firm = [
            join("$BUILD_DIR", "firmware_00000.bin"),
            join("$BUILD_DIR", "firmware_40000.bin")
        ]
    else:
        target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    if "FRAMEWORK" not in env:
        target_firm = env.ElfToBin(
            [join("$BUILD_DIR", "firmware_00000"),
             join("$BUILD_DIR", "firmware_40000")], target_elf)
    else:
        target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload firmware
#

upload = env.Alias(["upload", "uploadlazy"], target_firm,
                   [BeforeUpload, "$UPLOADCMD"])
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])
