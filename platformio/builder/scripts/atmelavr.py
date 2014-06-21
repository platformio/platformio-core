# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join

from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default,
                          DefaultEnvironment, Exit, SConscript,
                          SConscriptChdir)

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

if "BUILD_FLAGS" in env:
    env.MergeFlags(env['BUILD_FLAGS'])

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
    join(env.subst("$PLATFORMTOOLS_DIR"), "toolchain", "bin")
)

BUILT_LIBS = []

#
# Process framework script
#

if "FRAMEWORK" in env:
    SConscriptChdir(0)
    flibs = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts",
                                      "frameworks", "${FRAMEWORK}.py")),
                       exports="env")
    BUILT_LIBS += flibs

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(BUILT_LIBS + ["m"])

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
Default([target_elf, target_hex])

# check for $UPLOAD_PORT variable
is_uptarget = ("eep" in COMMAND_LINE_TARGETS or "upload" in
               COMMAND_LINE_TARGETS)
if is_uptarget and not env.subst("$UPLOAD_PORT"):
    Exit("Please specify 'upload_port'")
