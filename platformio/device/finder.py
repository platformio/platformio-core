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
from functools import lru_cache

import click
import serial

from platformio.compat import IS_WINDOWS
from platformio.device.list.util import list_logical_devices, list_serial_ports
from platformio.fs import get_platformio_udev_rules_path
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.factory import PlatformFactory
from platformio.util import retry

BLACK_MAGIC_HWIDS = [
    "1D50:6018",
]


def parse_udev_rules_hwids(path):
    result = []
    with open(path, mode="r", encoding="utf8") as fp:
        for line in fp.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            attrs = {}
            for attr in line.split(","):
                attr = attr.replace("==", "=").replace('"', "").strip()
                if "=" not in attr:
                    continue
                name, value = attr.split("=", 1)
                attrs[name] = value
            hwid = "%s:%s" % (
                attrs.get("ATTRS{idVendor}", "*"),
                attrs.get("ATTRS{idProduct}", "*"),
            )
            if hwid != "*:*":
                result.append(hwid.upper())
    return result


def is_pattern_port(port):
    if not port:
        return False
    return set(["*", "?", "[", "]"]) & set(port)


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


def is_serial_port_ready(port, timeout=1):
    try:
        serial.Serial(port, timeout=timeout).close()
        return True
    except:  # pylint: disable=bare-except
        pass
    return False


class SerialPortFinder:
    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        board_config=None,
        upload_protocol=None,
        ensure_ready=False,
        prefer_gdb_port=False,
        timeout=2,
        verbose=False,
    ):
        self.board_config = board_config
        self.upload_protocol = upload_protocol
        self.ensure_ready = ensure_ready
        self.prefer_gdb_port = prefer_gdb_port
        self.timeout = timeout
        self.verbose = verbose

    @staticmethod
    def normalize_board_hwid(value):
        if isinstance(value, (list, tuple)):
            value = ("%s:%s" % (value[0], value[1])).replace("0x", "")
        return value.upper()

    @staticmethod
    def match_serial_port(pattern):
        for item in list_serial_ports():
            if fnmatch(item["port"], pattern):
                return item["port"]
        return None

    @staticmethod
    def match_device_hwid(patterns):
        if not patterns:
            return None
        for item in list_serial_ports(as_objects=True):
            if not item.vid or not item.pid:
                continue
            hwid = "{:04X}:{:04X}".format(item.vid, item.pid)
            for pattern in patterns:
                if fnmatch(hwid, pattern):
                    return item
        return None

    def find(self, initial_port=None):
        if initial_port:
            if not is_pattern_port(initial_port):
                return initial_port
            return self.match_serial_port(initial_port)

        if self.upload_protocol and self.upload_protocol.startswith("blackmagic"):
            return self._find_blackmagic_port()

        device = None
        if self.board_config and self.board_config.get("build.hwids", []):
            device = self._find_board_device()
        if not device:
            device = self._find_known_device()
        if device:
            return self._reveal_device_port(device)

        # pick the best PID:VID USB device
        port = best_port = None
        for item in list_serial_ports():
            if self.ensure_ready and not is_serial_port_ready(item["port"]):
                continue
            port = item["port"]
            if "VID:PID" in item["hwid"]:
                best_port = port
        return best_port or port

    def _reveal_device_port(self, device):
        candidates = []
        for item in list_serial_ports(as_objects=True):
            if item.vid == device.vid and item.pid == device.pid:
                candidates.append(item)
        if len(candidates) <= 1:
            return device.device
        for item in candidates:
            if ("GDB" if self.prefer_gdb_port else "UART") in item.description:
                return item.device
        candidates = sorted(candidates, key=lambda item: item.device)
        # first port is GDB? BlackMagic, ESP-Prog
        return candidates[0 if self.prefer_gdb_port else -1].device

    def _find_blackmagic_port(self):
        device = self.match_device_hwid(BLACK_MAGIC_HWIDS)
        if not device:
            return None
        port = self._reveal_device_port(device)
        if IS_WINDOWS and port.startswith("COM") and len(port) > 4:
            return "\\\\.\\%s" % port
        return port

    def _find_board_device(self):
        hwids = [
            self.normalize_board_hwid(hwid)
            for hwid in self.board_config.get("build.hwids", [])
        ]
        try:

            @retry(timeout=self.timeout)
            def wrapper():
                device = self.match_device_hwid(hwids)
                if device:
                    return device
                raise retry.RetryNextException()

            return wrapper()
        except retry.RetryStopException:
            pass

        if self.verbose:
            click.secho(
                "TimeoutError: Could not automatically find serial port "
                "for the `%s` board based on the declared HWIDs=%s"
                % (self.board_config.get("name", "unknown"), hwids),
                fg="yellow",
                err=True,
            )

        return None

    def _find_known_device(self):
        hwids = list(BLACK_MAGIC_HWIDS)

        # load from UDEV rules
        udev_rules_path = get_platformio_udev_rules_path()
        if os.path.isfile(udev_rules_path):
            hwids.extend(parse_udev_rules_hwids(udev_rules_path))

        @lru_cache(maxsize=1)
        def _fetch_hwids_from_platforms():
            """load from installed dev-platforms"""
            result = []
            for platform in PlatformPackageManager().get_installed():
                p = PlatformFactory.new(platform)
                for board_config in p.get_boards().values():
                    for board_hwid in board_config.get("build.hwids", []):
                        board_hwid = self.normalize_board_hwid(board_hwid)
                        if board_hwid not in result:
                            result.append(board_hwid)
            return result

        try:

            @retry(timeout=self.timeout)
            def wrapper():
                device = self.match_device_hwid(hwids)
                if not device:
                    device = self.match_device_hwid(_fetch_hwids_from_platforms())
                if device:
                    return device
                raise retry.RetryNextException()

            return wrapper()
        except retry.RetryStopException:
            pass

        if self.verbose:
            click.secho(
                "TimeoutError: Could not automatically find serial port "
                "based on the known UART bridges",
                fg="yellow",
                err=True,
            )

        return None
