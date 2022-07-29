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

from platformio.debug.config.base import DebugConfigBase
from platformio.debug.exception import DebugInvalidOptionsError
from platformio.device.finder import SerialPortFinder, is_pattern_port


class BlackmagicDebugConfig(DebugConfigBase):

    GDB_INIT_SCRIPT = """
define pio_reset_halt_target
    set language c
    set *0xE000ED0C = 0x05FA0004
    set $busy = (*0xE000ED0C & 0x4)
    while ($busy)
        set $busy = (*0xE000ED0C & 0x4)
    end
    set language auto
end

define pio_reset_run_target
    pio_reset_halt_target
end

target extended-remote $DEBUG_PORT
monitor swdp_scan
attach 1
set mem inaccessible-by-default off
$LOAD_CMDS
$INIT_BREAK

set language c
set *0xE000ED0C = 0x05FA0004
set $busy = (*0xE000ED0C & 0x4)
while ($busy)
    set $busy = (*0xE000ED0C & 0x4)
end
set language auto
"""

    @property
    def port(self):
        # pylint: disable=assignment-from-no-return
        initial_port = DebugConfigBase.port.fget(self)
        if initial_port and not is_pattern_port(initial_port):
            return initial_port
        port = SerialPortFinder(
            board_config=self.board_config,
            upload_protocol=self.tool_name,
            prefer_gdb_port=True,
        ).find(initial_port)
        if port:
            return port
        raise DebugInvalidOptionsError(
            "Please specify `debug_port` for the working environment"
        )

    @port.setter
    def port(self, value):
        self._port = value
