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

import os
from fnmatch import fnmatch

import serial

from platformio.compat import IS_WINDOWS
from platformio.device.list import list_logical_devices, list_serial_ports


def is_pattern_port(port):
    if not port:
        return False
    return set(["*", "?", "[", "]"]) & set(port)


def match_serial_port(pattern):
    for item in list_serial_ports():
        if fnmatch(item["port"], pattern):
            return item["port"]
    return None


def is_serial_port_ready(port, timeout=1):
    try:
        serial.Serial(port, timeout=timeout).close()
        return True
    except:  # pylint: disable=bare-except
        pass
    return False


def find_serial_port(
    initial_port, board_config=None, upload_protocol=None, ensure_ready=False
):
    if initial_port:
        if not is_pattern_port(initial_port):
            return initial_port
        return match_serial_port(initial_port)
    port = None
    if upload_protocol and upload_protocol.startswith("blackmagic"):
        port = find_blackmagic_serial_port()
    if not port and board_config:
        port = find_board_serial_port(board_config)
    if port:
        return port

    # pick the last PID:VID USB device
    usb_port = None
    for item in list_serial_ports():
        if ensure_ready and not is_serial_port_ready(item["port"]):
            continue
        port = item["port"]
        if "VID:PID" in item["hwid"]:
            usb_port = port
    return usb_port or port


def find_blackmagic_serial_port():
    for item in list_serial_ports():
        port = item["port"]
        if IS_WINDOWS and port.startswith("COM") and len(port) > 4:
            port = "\\\\.\\%s" % port
        if "GDB" in item["description"]:
            return port
    return None


def find_board_serial_port(board_config):
    board_hwids = board_config.get("build.hwids", [])
    if not board_hwids:
        return None
    for item in list_serial_ports(filter_hwid=True):
        port = item["port"]
        for hwid in board_hwids:
            hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
            if hwid_str in item["hwid"]:
                return port
    return None


def find_mbed_disk(initial_port):
    msdlabels = ("mbed", "nucleo", "frdm", "microbit")
    for item in list_logical_devices():
        if item["path"].startswith("/net"):
            continue
        if (
            initial_port
            and is_pattern_port(initial_port)
            and not fnmatch(item["path"], initial_port)
        ):
            continue
        mbed_pages = [os.path.join(item["path"], n) for n in ("mbed.htm", "mbed.html")]
        if any(os.path.isfile(p) for p in mbed_pages):
            return item["path"]
        if item["name"] and any(l in item["name"].lower() for l in msdlabels):
            return item["path"]
    return None
