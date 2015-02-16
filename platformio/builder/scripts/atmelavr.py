# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join
from time import sleep

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment, Exit)

from platformio.util import get_serialports

env = DefaultEnvironment()

env.Replace(
    AR="avr-ar",
    AS="avr-gcc",
    CC="avr-gcc",
    CXX="avr-g++",
    OBJCOPY="avr-objcopy",
    RANLIB="avr-ranlib",
    SIZETOOL="avr-size",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-c",
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

    SIZEPRINTCMD='"$SIZETOOL" --mcu=$BOARD_MCU -C -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-avrdude", "avrdude"),
    UPLOADERFLAGS=[
        "-q",  # suppress progress output
        "-D",  # disable auto erase for flash memory
        "-p", "$BOARD_MCU",
        "-C",
        '"%s"' % join("$PIOPACKAGES_DIR", "tool-avrdude", "avrdude.conf"),
        "-c", "$UPLOAD_PROTOCOL"
    ],
    UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i',
    UPLOADEEPCMD='"$UPLOADER" $UPLOADERFLAGS -U eeprom:w:$SOURCES:i'
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


def before_upload(target, source, env):  # pylint: disable=W0613

    def _autodetect_upload_port():
        if "UPLOAD_PORT" not in env:
            for item in get_serialports():
                if "VID:PID" in item['hwid']:
                    print "Auto-detected UPLOAD_PORT: %s" % item['port']
                    env.Replace(UPLOAD_PORT=item['port'])
                    break

        if "UPLOAD_PORT" not in env:
            Exit("Error: Please specify `upload_port` for environment or use "
                 "global `--upload-port` option.\n")

    def _rpi_sysgpio(path, value):
        with open(path, "w") as f:
            f.write(str(value))

    if env.subst("$UPLOAD_PROTOCOL") != "usbtiny":
        _autodetect_upload_port()

    if env.subst("$BOARD") == "raspduino":
        _rpi_sysgpio("/sys/class/gpio/export", 18)
        _rpi_sysgpio("/sys/class/gpio/gpio18/direction", "out")
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 1)
        sleep(0.1)
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 0)
        _rpi_sysgpio("/sys/class/gpio/unexport", 18)
    else:
        upload_options = env.get("BOARD_OPTIONS", {}).get("upload", {})

        if not upload_options.get("disable_flushing", False):
            env.FlushSerialBuffer("$UPLOAD_PORT")

        before_ports = [i['port'] for i in get_serialports()]

        if (upload_options.get("use_1200bps_touch", False) and
                "UPLOAD_PORT" in env):
            env.TouchSerialPort("$UPLOAD_PORT", 1200)

        if upload_options.get("wait_for_upload_port", False):
            env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))


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
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .hex file
#

upload = env.Alias(["upload", "uploadlazy"], target_hex, [
    before_upload, "$UPLOADHEXCMD"])
AlwaysBuild(upload)

#
# Target: Upload .eep file
#

uploadeep = env.Alias("uploadeep", target_eep, [
    before_upload, "$UPLOADEEPCMD"])
AlwaysBuild(uploadeep)

#
# Setup default targets
#

Default([target_hex, target_size])
