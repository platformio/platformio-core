# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join
from time import sleep

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

from platformio.util import get_serialports


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621

    def _rpi_sysgpio(path, value):
        with open(path, "w") as f:
            f.write(str(value))

    if "micronucleus" in env['UPLOADER']:
        print "Please unplug/plug device ..."

    upload_options = env.get("BOARD_OPTIONS", {}).get("upload", {})

    if "usb" in env.subst("$UPLOAD_PROTOCOL"):
        upload_options['require_upload_port'] = False
        env.Replace(UPLOAD_SPEED=None)

    if env.subst("$UPLOAD_SPEED"):
        env.Append(UPLOADERFLAGS=[
            "-b", "$UPLOAD_SPEED",
            "-D"
        ])

    if not upload_options.get("require_upload_port", False):
        return

    env.AutodetectUploadPort()
    env.Append(UPLOADERFLAGS=["-P", "$UPLOAD_PORT"])

    if env.subst("$BOARD") == "raspduino":
        _rpi_sysgpio("/sys/class/gpio/export", 18)
        _rpi_sysgpio("/sys/class/gpio/gpio18/direction", "out")
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 1)
        sleep(0.1)
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 0)
        _rpi_sysgpio("/sys/class/gpio/unexport", 18)
    else:
        if not upload_options.get("disable_flushing", False):
            env.FlushSerialBuffer("$UPLOAD_PORT")

        before_ports = [i['port'] for i in get_serialports()]

        if upload_options.get("use_1200bps_touch", False):
            env.TouchSerialPort("$UPLOAD_PORT", 1200)

        if upload_options.get("wait_for_upload_port", False):
            env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))


env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "baseavr.py")))

if "digispark" in env.get(
        "BOARD_OPTIONS", {}).get("build", {}).get("core", ""):
    env.Replace(
        UPLOADER=join("$PIOPACKAGES_DIR", "tool-micronucleus", "micronucleus"),
        UPLOADERFLAGS=[
            "-c", "$UPLOAD_PROTOCOL",
            "--timeout", "60"
        ],
        UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
    )

else:
    env.Replace(
        UPLOADER=join("$PIOPACKAGES_DIR", "tool-avrdude", "avrdude"),
        UPLOADERFLAGS=[
            "-v",
            "-p", "$BOARD_MCU",
            "-C",
            '"%s"' % join("$PIOPACKAGES_DIR", "tool-avrdude", "avrdude.conf"),
            "-c", "$UPLOAD_PROTOCOL"
        ],

        UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i',
        UPLOADEEPCMD='"$UPLOADER" $UPLOADERFLAGS -U eeprom:w:$SOURCES:i'
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

#
# Target: Extract EEPROM data (from EEMEM directive) to .eep file
#

target_eep = env.Alias("eep", env.ElfToEep(join("$BUILD_DIR", "firmware"),
                                           target_elf))

#
# Target: Build the .hex file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.hex")
else:
    target_firm = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .hex file
#

upload = env.Alias(["upload", "uploadlazy"], target_firm,
                   [BeforeUpload, "$UPLOADHEXCMD"])
AlwaysBuild(upload)

#
# Target: Upload .eep file
#

uploadeep = env.Alias("uploadeep", target_eep, [
    BeforeUpload, "$UPLOADEEPCMD"])
AlwaysBuild(uploadeep)

#
# Setup default targets
#

Default([target_firm, target_size])
