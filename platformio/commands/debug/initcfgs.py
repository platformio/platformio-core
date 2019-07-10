# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

GDB_DEFAULT_INIT_CONFIG = """
define pio_reset_halt_target
    monitor reset halt
end

define pio_reset_target
    monitor reset
end

target extended-remote $DEBUG_PORT
$INIT_BREAK
pio_reset_halt_target
$LOAD_CMDS
monitor init
pio_reset_halt_target
"""

GDB_STUTIL_INIT_CONFIG = """
define pio_reset_halt_target
    monitor halt
    monitor reset
end

define pio_reset_target
    monitor reset
end

target extended-remote $DEBUG_PORT
$INIT_BREAK
pio_reset_halt_target
$LOAD_CMDS
pio_reset_halt_target
"""

GDB_JLINK_INIT_CONFIG = """
define pio_reset_halt_target
    monitor halt
    monitor reset
end

define pio_reset_target
    monitor reset
end

target extended-remote $DEBUG_PORT
$INIT_BREAK
pio_reset_halt_target
$LOAD_CMDS
pio_reset_halt_target
"""

GDB_BLACKMAGIC_INIT_CONFIG = """
define pio_reset_halt_target
    set language c
    set *0xE000ED0C = 0x05FA0004
    set $busy = (*0xE000ED0C & 0x4)
    while ($busy)
        set $busy = (*0xE000ED0C & 0x4)
    end
    set language auto
end

define pio_reset_target
    pio_reset_halt_target
end

target extended-remote $DEBUG_PORT
monitor swdp_scan
attach 1
set mem inaccessible-by-default off
$INIT_BREAK
$LOAD_CMDS

set language c
set *0xE000ED0C = 0x05FA0004
set $busy = (*0xE000ED0C & 0x4)
while ($busy)
    set $busy = (*0xE000ED0C & 0x4)
end
set language auto
"""

GDB_MSPDEBUG_INIT_CONFIG = """
define pio_reset_halt_target
end

define pio_reset_target
end

target extended-remote $DEBUG_PORT
$INIT_BREAK
monitor erase
$LOAD_CMDS
pio_reset_halt_target
"""

GDB_QEMU_INIT_CONFIG = """
define pio_reset_halt_target
    monitor system_reset
end

define pio_reset_target
    pio_reset_halt_target
end

target extended-remote $DEBUG_PORT
$INIT_BREAK
$LOAD_CMDS
pio_reset_halt_target
"""
