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

target extended-remote $_PORT
$_MONITOR_CMDS
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

    def _parse_port_config(self, port_string):
        """Parse port configuration string into port and optional commands.
        
        Format: port_path [cmd1] [cmd2] ...
        Supported commands: connect_srst, tpwr
        """
        if not port_string:
            return None, []

        parts = port_string.split()
        port = parts[0]
        commands = parts[1:] if len(parts) > 1 else []
        
        valid_commands = ["connect_srst", "tpwr"]
        monitor_cmds = []
        
        for cmd in commands:
            if cmd not in valid_commands:
                continue
            if cmd == "connect_srst":
                monitor_cmds.append("monitor connect_srst enable")
            elif cmd == "tpwr":
                monitor_cmds.append("monitor tpwr enable")
        
        return port, monitor_cmds

    @property
    def port(self):
        # pylint: disable=assignment-from-no-return
        initial_port = DebugConfigBase.port.fget(self)
        if not initial_port:
            raise DebugInvalidOptionsError(
                "Please specify `debug_port` for the working environment"
            )

        port, monitor_cmds = self._parse_port_config(initial_port)
        
        if not is_pattern_port(port):
            self._port = port
            self._monitor_cmds = monitor_cmds
            return port
            
        found_port = SerialPortFinder(
            board_config=self.board_config,
            upload_protocol=self.tool_name,
            prefer_gdb_port=True,
        ).find(port)
        
        if found_port:
            self._port = found_port
            self._monitor_cmds = monitor_cmds
            return found_port
            
        raise DebugInvalidOptionsError(
            "Please specify a valid `debug_port` for the working environment"
        )

    @port.setter
    def port(self, value):
        self._port = value
        
    def get_init_script(self):
        """Override to insert monitor commands before scan."""
        script = self.GDB_INIT_SCRIPT
        script = script.replace("$_PORT", self._port)
        
        monitor_cmds = getattr(self, "_monitor_cmds", [])
        script = script.replace("$_MONITOR_CMDS", "\n".join(monitor_cmds))
        
        # Handle the standard replacements
        script = script.replace(
            "$LOAD_CMDS",
            "load" if self.prog_path else ""
        )
        script = script.replace(
            "$INIT_BREAK",
            "break main" if self.init_break else ""
        )
        
        return script
