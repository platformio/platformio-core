# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Base for Atmel AVR series of microcontrollers
"""

from SCons.Script import Builder, DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    AR="avr-ar",
    AS="avr-gcc",
    CC="avr-gcc",
    CXX="avr-g++",
    OBJCOPY="avr-objcopy",
    RANLIB="avr-ranlib",
    SIZETOOL="avr-size",

    ASCOM=("$AS -o $TARGET -c -x assembler-with-cpp "
           "$CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES"),

    ARFLAGS=["rcs"],

    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-MMD",  # output dependency info
        "-mmcu=$BOARD_MCU"
    ],

    CXXFLAGS=[
        "-fno-exceptions",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU"
    ],

    LINKFLAGS=[
        "-Os",
        "-mmcu=$BOARD_MCU",
        "-Wl,--gc-sections"
    ],

    SIZEPRINTCMD='"$SIZETOOL" --mcu=$BOARD_MCU -C -d $SOURCES'
)

if "UPLOAD_SPEED" in env:
    env.Append(UPLOADERFLAGS=["-b", "$UPLOAD_SPEED"])
if env.subst("$UPLOAD_PROTOCOL") != "usbtiny":
    env.Append(UPLOADERFLAGS=["-P", "$UPLOAD_PORT"])

env.Append(
    BUILDERS=dict(
        ElfToEep=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-j",
                ".eeprom",
                '--set-section-flags=.eeprom="alloc,load"',
                "--no-change-warnings",
                "--change-section-lma",
                ".eeprom=0",
                "$SOURCES",
                "$TARGET"]),
            suffix=".eep"
        ),

        ElfToHex=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-R",
                ".eeprom",
                "$SOURCES",
                "$TARGET"]),
            suffix=".hex"
        )
    )
)
