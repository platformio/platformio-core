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
    Builder for Atmel AVR series of microcontrollers
"""

from os.path import join
from time import sleep

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

from platformio.util import get_serialports


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621

    if "program" in COMMAND_LINE_TARGETS:
        return

    if "micronucleus" in env['UPLOADER']:
        print "Please unplug/plug device ..."

    upload_options = env.get("BOARD_OPTIONS", {}).get("upload", {})

    # Deprecated: compatibility with old projects. Use `program` instead
    if "usb" in env.subst("$UPLOAD_PROTOCOL"):
        upload_options['require_upload_port'] = False
        env.Replace(UPLOAD_SPEED=None)

    if env.subst("$UPLOAD_SPEED"):
        env.Append(UPLOADERFLAGS=["-b", "$UPLOAD_SPEED"])

    if upload_options and not upload_options.get("require_upload_port", False):
        return

    env.AutodetectUploadPort()
    env.Append(UPLOADERFLAGS=["-P", '"$UPLOAD_PORT"'])

    if env.subst("$BOARD") == "raspduino":

        def _rpi_sysgpio(path, value):
            with open(path, "w") as f:
                f.write(str(value))

        _rpi_sysgpio("/sys/class/gpio/export", 18)
        _rpi_sysgpio("/sys/class/gpio/gpio18/direction", "out")
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 1)
        sleep(0.1)
        _rpi_sysgpio("/sys/class/gpio/gpio18/value", 0)
        _rpi_sysgpio("/sys/class/gpio/unexport", 18)
    else:
        if not upload_options.get("disable_flushing", False):
            env.FlushSerialBuffer("$UPLOAD_PORT")

        before_ports = get_serialports()

        if upload_options.get("use_1200bps_touch", False):
            env.TouchSerialPort("$UPLOAD_PORT", 1200)

        if upload_options.get("wait_for_upload_port", False):
            env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))


env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "baseavr.py")))

env.Append(
    CFLAGS=[
        "-std=gnu11"
    ],

    CXXFLAGS=[
        "-std=gnu++11"
    ]
)

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
        UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS -D -U flash:w:$SOURCES:i',
        UPLOADEEPCMD='"$UPLOADER" $UPLOADERFLAGS -U eeprom:w:$SOURCES:i',
        PROGRAMHEXCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i'
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

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
# Target: Upload EEPROM data (from EEMEM directive)
#

uploadeep = env.Alias(
    "uploadeep",
    env.ElfToEep(join("$BUILD_DIR", "firmware"), target_elf),
    [BeforeUpload, "$UPLOADEEPCMD"])
AlwaysBuild(uploadeep)

#
# Target: Upload firmware using external programmer
#

program = env.Alias("program", target_firm, [BeforeUpload, "$PROGRAMHEXCMD"])
AlwaysBuild(program)

#
# Setup default targets
#

Default([target_firm, target_size])
