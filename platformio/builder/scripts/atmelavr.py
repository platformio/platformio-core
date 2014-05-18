# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers

    Fully compatible with Arduino programming language (based on Wiring)
"""

from os.path import join

from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default,
                          DefaultEnvironment, Exit)

#
# SETUP ENVIRONMENT
#

env = DefaultEnvironment()

BOARD_OPTIONS = env.ParseBoardOptions(join("$PLATFORM_DIR", "boards.txt"),
                                      "${BOARD}")
env.Replace(
    ARDUINO_VERSION=open(join(env.subst("$PLATFORM_DIR"),
                              "version.txt")).read().replace(".", "").strip(),

    BOARD_MCU=BOARD_OPTIONS['build.mcu'],
    BOARD_F_CPU=BOARD_OPTIONS['build.f_cpu'],
    BOARD_VID=BOARD_OPTIONS.get("build.vid", "0"),
    BOARD_PID=BOARD_OPTIONS.get("build.pid", "0"),

    AR="avr-ar",
    AS="avr-as",
    CC="avr-gcc",
    CXX="avr-g++",
    OBJCOPY="avr-objcopy",
    RANLIB="avr-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "assembler-with-cpp",
        "-mmcu=$BOARD_MCU",
        "-DF_CPU=$BOARD_F_CPU",
        "-DUSB_VID=$BOARD_VID",
        "-DUSB_PID=$BOARD_PID",
        "-DARDUINO=$ARDUINO_VERSION"
    ],
    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-fno-exceptions",
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-mmcu=$BOARD_MCU",
        "-DF_CPU=$BOARD_F_CPU",
        "-MMD",  # output dependancy info
        "-DUSB_VID=$BOARD_VID",
        "-DUSB_PID=$BOARD_PID",
        "-DARDUINO=$ARDUINO_VERSION"
    ],
    CFLAGS=["-std=gnu99"],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections" + (",--relax" if BOARD_OPTIONS['build.mcu'] ==
                               "atmega2560" else ""),
        "-mmcu=$BOARD_MCU",
        "-lm"
    ],

    CPPPATH=[
        "$PLATFORMCORE_DIR",
        join("$PLATFORM_DIR", "variants", BOARD_OPTIONS['build.variant'])
    ],

    UPLOADER="avrdude",
    UPLOADERFLAGS=[
        "-V",  # do not verify
        "-q",  # suppress progress output
        "-D",  # disable auto erase for flash memory
        "-p", "$BOARD_MCU",
        "-C", join("$PLATFORMTOOLS_DIR", "avr", "etc", "avrdude.conf"),
        "-c", ("stk500v1" if BOARD_OPTIONS['upload.protocol'] == "stk500" else
               BOARD_OPTIONS['upload.protocol']),
        "-b", BOARD_OPTIONS['upload.speed'],
        "-P", "${UPLOAD_PORT}"
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

env.PrependENVPath(
    "PATH",
    join(env.subst("$PLATFORMTOOLS_DIR"), "avr", "bin")
)


#
# Target: Build Core Library
#

target_corelib = env.BuildCoreLibrary()


#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware([target_corelib])


#
# Target: Extract EEPROM data (from EEMEM directive) to .eep file
#

target_eep = env.ElfToEep(join("$BUILD_DIR", "firmware"), target_elf)


#
# Target: Build the .hex file
#

target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)


#
# Target: Upload .eep file
#

eep = env.Alias("eep", target_eep, [
    lambda target, source, env: env.ResetDevice(), "$UPLOADEEPCMD"])
AlwaysBuild(eep)


#
# Target: Upload .hex file
#

upload = env.Alias("upload", target_hex, [
    lambda target, source, env: env.ResetDevice(), "$UPLOADHEXCMD"])
AlwaysBuild(upload)


#
# Target: Define targets
#

env.Alias("build-eep", [target_eep])
Default([target_corelib, target_elf, target_hex])

# check for $UPLOAD_PORT variable
is_uptarget = ("eep" in COMMAND_LINE_TARGETS or "upload" in
               COMMAND_LINE_TARGETS)
if is_uptarget and not env.subst("$UPLOAD_PORT"):
    Exit("Please specify 'upload_port'")
