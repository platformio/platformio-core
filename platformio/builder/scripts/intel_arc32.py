# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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
    Builder for Intel ARC32 microcontrollers
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)

env = DefaultEnvironment()


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621

    if env.get("BOARD_OPTIONS", {}).get("upload", {}).get(
            "use_1200bps_touch", False):
        env.TouchSerialPort("$UPLOAD_PORT", 1200)


env.Replace(
    AR="arc-elf32-ar",
    AS="arc-elf32-as",
    CC="arc-elf32-gcc",
    CXX="arc-elf32-g++",
    OBJCOPY="arc-elf32-objcopy",
    RANLIB="arc-elf32-ranlib",
    SIZETOOL="arc-elf32-size",

    ARFLAGS=["rcs"],

    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-g",
        "-Os",
        "-ffunction-sections",
        "-fdata-sections",
        "-Wall",
        "-mlittle-endian",
        "-mcpu=${BOARD_OPTIONS['build']['cpu']}",
        "-fno-reorder-functions",
        "-fno-asynchronous-unwind-tables",
        "-fno-omit-frame-pointer",
        "-fno-defer-pop",
        "-Wno-unused-but-set-variable",
        "-Wno-main",
        "-ffreestanding",
        "-fno-stack-protector",
        "-mno-sdata",
        "-fsigned-char"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-std=c++11",
        "-fno-exceptions"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU",
        "ARDUINO_ARC32_TOOLS",
        "__CPU_ARC__",
        "CLOCK_SPEED=%d" % (
            int(env.subst("${BOARD_OPTIONS['build']['f_cpu']}").replace(
                "L", ""))/1000000),
        "CONFIG_SOC_GPIO_32",
        "CONFIG_SOC_GPIO_AON",
        "INFRA_MULTI_CPU_SUPPORT",
        "CFW_MULTI_CPU_SUPPORT",
        "HAS_SHARED_MEM"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections",
        "-Wl,-X",
        "-Wl,-N",
        "-Wl,-mcpu=${BOARD_OPTIONS['build']['cpu']}",
        "-Wl,-marcelf",
        "-static",
        "-nostdlib",
        "-nodefaultlibs",
        "-nostartfiles",
        "-Wl,--whole-archive",
        "-larc32drv_arduino101",
        "-Wl,--no-whole-archive"
    ],

    LIBS=["nsim", "c", "m", "gcc"],

    SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-arduino101load", "arduino101load"),
    UPLOADERFLAGS=[
        '"$UPLOAD_PORT"'
    ],
    DFUUTIL=join("$PIOPACKAGES_DIR", "tool-arduino101load", "dfu-util"),
    UPLOADCMD='"$UPLOADER" "$DFUUTIL" $SOURCES $UPLOADERFLAGS verbose',

    PROGNAME="firmware",
    PROGSUFFIX=".elf"
)


env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-S",
                "-O",
                "binary",
                "-R",
                ".note",
                "-R",
                ".comment",
                "-R",
                "COMMON",
                "-R",
                ".eh_frame",
                "$SOURCES",
                "$TARGET"]),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-S",
                "-O",
                "binary",
                "-R",
                ".note",
                "-R",
                ".comment",
                "-R",
                "COMMON",
                "-R",
                ".eh_frame",
                "$SOURCES",
                "$TARGET"]),
            suffix=".hex"
        )
    )
)

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

#
# Target: Build the .bin
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
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
                   [env.AutodetectUploadPort, BeforeUpload, "$UPLOADCMD"])
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])
