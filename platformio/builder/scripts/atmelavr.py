# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join
from time import sleep

from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default,
                          DefaultEnvironment, Exit)

from platformio.util import get_serialports, reset_serialport

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
        # "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-MMD",  # output dependency info
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


def reset_device():

    def rpi_sysgpio(path, value):
        with open(path, "w") as f:
            f.write(str(value))

    if env.subst("$BOARD") == "raspduino":
        rpi_sysgpio("/sys/class/gpio/export", 18)
        rpi_sysgpio("/sys/class/gpio/gpio18/direction", "out")
        rpi_sysgpio("/sys/class/gpio/gpio18/value", 1)
        sleep(0.1)
        rpi_sysgpio("/sys/class/gpio/gpio18/value", 0)
        rpi_sysgpio("/sys/class/gpio/unexport", 18)
    else:
        return reset_serialport(env.subst("$UPLOAD_PORT"))


CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(CORELIBS + ["m"])

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
    lambda target, source, env: reset_device(), "$UPLOADHEXCMD"])
AlwaysBuild(upload)

#
# Target: Upload .eep file
#

uploadeep = env.Alias("uploadeep", target_eep, [
    lambda target, source, env: reset_device(), "$UPLOADEEPCMD"])
AlwaysBuild(uploadeep)

#
# Check for $UPLOAD_PORT variable
#

is_uptarget = (set(["upload", "uploadlazy", "uploadeep"]) &
               set(COMMAND_LINE_TARGETS))

if is_uptarget:
    # try autodetect upload port
    if "UPLOAD_PORT" not in env:
        for item in get_serialports():
            if "VID:PID" in item['hwid']:
                print ("Auto-detected UPLOAD_PORT: %s" % item['port'])
                env['UPLOAD_PORT'] = item['port']
                break

    if "UPLOAD_PORT" not in env:
        Exit("Please specify environment 'upload_port' or use global "
             "--upload-port option.")

#
# Setup default targets
#

Default(target_hex)
