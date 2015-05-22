# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Espressif MCUs
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()


env = DefaultEnvironment()

env.Replace(
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
        "-std=c99",
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
        "-Wl,-static"
    ],

    SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-esptool", "esptool"),
    UPLOADERFLAGS=[
        "-vv",
        "-cd", "ck",
        "-cb", "$UPLOAD_SPEED",
        "-cp", "$UPLOAD_PORT",
        "-ca", "0x00000",
        "-cf", "${SOURCES[0]}",
        "-ca", "0x10000",
        "-cf", "${SOURCES[1]}"
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS'
)

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$UPLOADER",
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

#
# Configure SDK
#

if "FRAMEWORK" not in env:
    env.Append(
        CPPPATH=[
            join("$PIOPACKAGES_DIR", "sdk-esp8266", "include"),
            "$PROJECTSRC_DIR"
        ],
        LIBPATH=[join("$PIOPACKAGES_DIR", "sdk-esp8266", "lib")]
    )
    env.Replace(
        LDSCRIPT_PATH=join(
            "$PIOPACKAGES_DIR", "sdk-esp8266", "ld", "eagle.app.v6.ld"),
        LIBS=["c", "gcc", "phy", "pp", "net80211", "lwip", "wpa", "main",
              "json", "upgrade", "smartconfig", "at", "ssl"]
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware()

#
# Target: Build the .hex
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    target_firm = env.ElfToBin(
        [join("$BUILD_DIR", "firmware_00000"),
         join("$BUILD_DIR", "firmware_10000")], target_elf)


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
