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
    Builder for Teensy boards
"""

from os.path import isfile, join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

env = DefaultEnvironment()

if env.get("BOARD_OPTIONS", {}).get("build", {}).get("core") == "teensy":
    SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "baseavr.py")))
elif env.get("BOARD_OPTIONS", {}).get("build", {}).get("core") == "teensy3":
    SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))
    env.Append(
        LINKFLAGS=[
            "-Wl,--defsym=__rtc_localtime=$UNIX_TIME",
            "-fsingle-precision-constant",
            "--specs=nano.specs"
        ],
        CCFLAGS=[
            "-fsingle-precision-constant"
        ]
    )

env.Append(
    CPPDEFINES=[
        "USB_SERIAL",
        "LAYOUT_US_ENGLISH"
    ],

    CXXFLAGS=[
        "-std=gnu++0x",
        "-felide-constructors"
    ]
)

if isfile(env.subst(join(
        "$PIOPACKAGES_DIR", "tool-teensy", "teensy_loader_cli"))):
    env.Append(
        UPLOADER=join(
            "$PIOPACKAGES_DIR", "tool-teensy", "teensy_loader_cli"),
        UPLOADERFLAGS=[
            "-mmcu=$BOARD_MCU",
            "-w",  # wait for device to apear
            "-s",  # soft reboot if device not online
            "-v"   # verbose output
        ],
        UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
    )
else:
    env.Append(
        REBOOTER=join(
            "$PIOPACKAGES_DIR", "tool-teensy", "teensy_reboot"),
        UPLOADER=join(
            "$PIOPACKAGES_DIR", "tool-teensy", "teensy_post_compile"),
        UPLOADERFLAGS=[
            "-file=firmware",
            '-path="$BUILD_DIR"',
            '-tools="%s"' % join("$PIOPACKAGES_DIR", "tool-teensy")
        ],
        UPLOADHEXCMD='"$UPLOADER" $UPLOADERFLAGS'
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

#
# Target: Build the firmware file
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
# Target: Upload by default firmware file
#

upload = env.Alias(
    ["upload", "uploadlazy"], target_firm,
    ["$UPLOADHEXCMD"] + (["$REBOOTER"] if "REBOOTER" in env else []))
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])
