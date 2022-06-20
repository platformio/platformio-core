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

import click
import serial

from platformio.compat import IS_MACOS, IS_WINDOWS
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


def normalize_board_hwid(value):
    if isinstance(value, (list, tuple)):
        value = ("%s:%s" % (value[0], value[1])).replace("0x", "")
    return value.upper()


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


def find_serial_port(  # pylint: disable=too-many-arguments
    initial_port,
    board_config=None,
    upload_protocol=None,
    ensure_ready=False,
    prefer_gdb_port=False,
    timeout=2,
):
    if initial_port:
        if not is_pattern_port(initial_port):
            return initial_port
        return match_serial_port(initial_port)

    if upload_protocol and upload_protocol.startswith("blackmagic"):
        return find_blackmagic_serial_port(prefer_gdb_port, timeout)
    if board_config and board_config.get("build.hwids", []):
        return find_board_serial_port(board_config, timeout)
    port = find_known_uart_port(ensure_ready, timeout)
    if port:
        return port

    # pick the best PID:VID USB device
    best_port = None
    for item in list_serial_ports():
        if ensure_ready and not is_serial_port_ready(item["port"]):
            continue
        port = item["port"]
        if "VID:PID" in item["hwid"]:
            best_port = port
    return best_port or port


def find_blackmagic_serial_port(prefer_gdb_port=False, timeout=0):
    try:

        @retry(timeout=timeout)
        def wrapper():
            candidates = []
            for item in list_serial_ports(filter_hwid=True):
                if (
                    not any(hwid in item["hwid"].upper() for hwid in BLACK_MAGIC_HWIDS)
                    and not "Black Magic" in item["description"]
                ):
                    continue
                if (
                    IS_WINDOWS
                    and item["port"].startswith("COM")
                    and len(item["port"]) > 4
                ):
                    item["port"] = "\\\\.\\%s" % item["port"]
                candidates.append(item)

            if not candidates:
                raise retry.RetryNextException()

            for item in candidates:
                if ("GDB" if prefer_gdb_port else "UART") in item["description"]:
                    return item["port"]
            if IS_MACOS:
                # 1 - GDB, 3 - UART
                for item in candidates:
                    if item["port"].endswith("1" if prefer_gdb_port else "3"):
                        return item["port"]

            candidates = sorted(candidates, key=lambda item: item["port"])
            return (
                candidates[0]  # first port is GDB?
                if len(candidates) == 1 or prefer_gdb_port
                else candidates[1]
            )["port"]

        return wrapper()
    except retry.RetryStopException:
        pass
    return None


def find_board_serial_port(board_config, timeout=0):
    hwids = board_config.get("build.hwids", [])
    try:

        @retry(timeout=timeout)
        def wrapper():
            for item in list_serial_ports(filter_hwid=True):
                hwid = item["hwid"].upper()
                for board_hwid in hwids:
                    if normalize_board_hwid(board_hwid) in hwid:
                        return item["port"]
            raise retry.RetryNextException()

        return wrapper()
    except retry.RetryStopException:
        pass

    click.secho(
        "TimeoutError: Could not automatically find serial port "
        "for the `%s` board based on the declared HWIDs=%s"
        % (board_config.get("name", "unknown"), hwids),
        fg="yellow",
        err=True,
    )

    return None


def find_known_uart_port(ensure_ready=False, timeout=0):
    known_hwids = list(BLACK_MAGIC_HWIDS)

    # load from UDEV rules
    udev_rules_path = get_platformio_udev_rules_path()
    if os.path.isfile(udev_rules_path):
        known_hwids.extend(parse_udev_rules_hwids(udev_rules_path))

    # load from installed dev-platforms
    for platform in PlatformPackageManager().get_installed():
        p = PlatformFactory.new(platform)
        for board_config in p.get_boards().values():
            for board_hwid in board_config.get("build.hwids", []):
                board_hwid = normalize_board_hwid(board_hwid)
                if board_hwid not in known_hwids:
                    known_hwids.append(board_hwid)

    try:

        @retry(timeout=timeout)
        def wrapper():
            for item in list_serial_ports(as_objects=True):
                if not item.vid or not item.pid:
                    continue
                hwid = "{:04X}:{:04X}".format(item.vid, item.pid)
                for pattern in known_hwids:
                    if fnmatch(hwid, pattern) and (
                        not ensure_ready or is_serial_port_ready(item.device)
                    ):
                        return item.device
            raise retry.RetryNextException()

        return wrapper()
    except retry.RetryStopException:
        pass

    click.secho(
        "TimeoutError: Could not automatically find serial port "
        "based on the known UART bridges",
        fg="yellow",
        err=True,
    )

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
