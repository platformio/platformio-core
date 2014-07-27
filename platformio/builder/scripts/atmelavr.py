# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join

from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default,
                          DefaultEnvironment, Exit)

from platformio.util import reset_serialport


env = DefaultEnvironment()

env.Replace(
    AR="avr-ar",
    AS="avr-gcc",
    CC="avr-gcc",
    CXX="avr-g++",
    OBJCOPY="avr-objcopy",
    RANLIB="avr-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "assembler-with-cpp",
        "-mmcu=$BOARD_MCU"
    ],

    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-MMD",  # output dependancy info
        "-mmcu=$BOARD_MCU"
    ],

    CXXFLAGS=["-fno-exceptions"],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections",
        "-mmcu=$BOARD_MCU"
    ],

    UPLOADER=join("$PLATFORMTOOLS_DIR", "avrdude", "avrdude"),
    UPLOADERFLAGS=[
        "-V",  # do not verify
        "-q",  # suppress progress output
        "-D",  # disable auto erase for flash memory
        "-p", "$BOARD_MCU",
        "-C", join("$PLATFORMTOOLS_DIR", "avrdude", "avrdude.conf"),
        "-c", "$UPLOAD_PROTOCOL",
        "-b", "$UPLOAD_SPEED",
        "-P", "$UPLOAD_PORT"
    ],
    UPLOADHEXCMD="$UPLOADER $UPLOADERFLAGS -U flash:w:$SOURCES:i",
    UPLOADEEPCMD="$UPLOADER $UPLOADERFLAGS -U eeprom:w:$SOURCES:i"
)

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

BUILT_LIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(BUILT_LIBS + ["m"])

#
# Target: Extract EEPROM data (from EEMEM directive) to .eep file
#

target_eep = env.Alias("eep", env.ElfToEep(join("$BUILD_DIR", "firmware"),
                                           target_elf))

#
# Target: Build the .hex file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_hex = join("$BUILD_DIR", "firmware.hex")
else:
    target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Upload by default .hex file
#

upload = env.Alias(["upload", "uploadlazy"], target_hex, [
    lambda target, source, env: reset_serialport(env.subst("$UPLOAD_PORT")),
    "$UPLOADHEXCMD"])
AlwaysBuild(upload)

#
# Target: Upload .eep file
#

uploadeep = env.Alias("uploadeep", target_eep, [
    lambda target, source, env: reset_serialport(env.subst("$UPLOAD_PORT")),
    "$UPLOADEEPCMD"])
AlwaysBuild(uploadeep)

#
# Check for $UPLOAD_PORT variable
#

is_uptarget = (set(["upload", "uploadlazy", "uploadeep"]) &
               set(COMMAND_LINE_TARGETS))
if is_uptarget and not env.subst("$UPLOAD_PORT"):
    Exit("Please specify environment 'upload_port' or use global "
         "--upload-port option.")

#
# Setup default targets
#

Default(target_hex)
