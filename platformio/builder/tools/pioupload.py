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

from __future__ import absolute_import

import re
import sys
from fnmatch import fnmatch
from os import environ
from os.path import isfile, join
from shutil import copyfile
from time import sleep

from SCons.Script import ARGUMENTS  # pylint: disable=import-error
from serial import Serial, SerialException

from platformio import exception, fs, util
from platformio.compat import WINDOWS
from platformio.proc import exec_command

# pylint: disable=unused-argument


def FlushSerialBuffer(env, port):
    s = Serial(env.subst(port))
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def TouchSerialPort(env, port, baudrate):
    port = env.subst(port)
    print("Forcing reset using %dbps open/close on port %s" % (baudrate, port))
    try:
        s = Serial(port=port, baudrate=baudrate)
        s.setDTR(False)
        s.close()
    except:  # pylint: disable=bare-except
        pass
    sleep(0.4)  # DO NOT REMOVE THAT (required by SAM-BA based boards)


def WaitForNewSerialPort(env, before):
    print("Waiting for the new upload port...")
    prev_port = env.subst("$UPLOAD_PORT")
    new_port = None
    elapsed = 0
    before = [p["port"] for p in before]
    while elapsed < 5 and new_port is None:
        now = [p["port"] for p in util.get_serial_ports()]
        for p in now:
            if p not in before:
                new_port = p
                break
        before = now
        sleep(0.25)
        elapsed += 0.25

    if not new_port:
        for p in now:
            if prev_port == p:
                new_port = p
                break

    try:
        s = Serial(new_port)
        s.close()
    except SerialException:
        sleep(1)

    if not new_port:
        sys.stderr.write(
            "Error: Couldn't find a board on the selected port. "
            "Check that you have the correct port selected. "
            "If it is correct, try pressing the board's reset "
            "button after initiating the upload.\n"
        )
        env.Exit(1)

    return new_port


def AutodetectUploadPort(*args, **kwargs):
    env = args[0]

    def _get_pattern():
        if "UPLOAD_PORT" not in env:
            return None
        if set(["*", "?", "[", "]"]) & set(env["UPLOAD_PORT"]):
            return env["UPLOAD_PORT"]
        return None

    def _is_match_pattern(port):
        pattern = _get_pattern()
        if not pattern:
            return True
        return fnmatch(port, pattern)

    def _look_for_mbed_disk():
        msdlabels = ("mbed", "nucleo", "frdm", "microbit")
        for item in util.get_logical_devices():
            if item["path"].startswith("/net") or not _is_match_pattern(item["path"]):
                continue
            mbed_pages = [join(item["path"], n) for n in ("mbed.htm", "mbed.html")]
            if any(isfile(p) for p in mbed_pages):
                return item["path"]
            if item["name"] and any(l in item["name"].lower() for l in msdlabels):
                return item["path"]
        return None

    def _look_for_serial_port():
        port = None
        board_hwids = []
        upload_protocol = env.subst("$UPLOAD_PROTOCOL")
        if "BOARD" in env and "build.hwids" in env.BoardConfig():
            board_hwids = env.BoardConfig().get("build.hwids")
        for item in util.get_serial_ports(filter_hwid=True):
            if not _is_match_pattern(item["port"]):
                continue
            port = item["port"]
            if upload_protocol.startswith("blackmagic"):
                if WINDOWS and port.startswith("COM") and len(port) > 4:
                    port = "\\\\.\\%s" % port
                if "GDB" in item["description"]:
                    return port
            for hwid in board_hwids:
                hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if hwid_str in item["hwid"]:
                    return port
        return port

    if "UPLOAD_PORT" in env and not _get_pattern():
        print(env.subst("Use manually specified: $UPLOAD_PORT"))
        return

    if env.subst("$UPLOAD_PROTOCOL") == "mbed" or (
        "mbed" in env.subst("$PIOFRAMEWORK") and not env.subst("$UPLOAD_PROTOCOL")
    ):
        env.Replace(UPLOAD_PORT=_look_for_mbed_disk())
    else:
        try:
            fs.ensure_udev_rules()
        except exception.InvalidUdevRules as e:
            sys.stderr.write("\n%s\n\n" % e)
        env.Replace(UPLOAD_PORT=_look_for_serial_port())

    if env.subst("$UPLOAD_PORT"):
        print(env.subst("Auto-detected: $UPLOAD_PORT"))
    else:
        sys.stderr.write(
            "Error: Please specify `upload_port` for environment or use "
            "global `--upload-port` option.\n"
            "For some development platforms it can be a USB flash "
            "drive (i.e. /media/<user>/<device name>)\n"
        )
        env.Exit(1)


def UploadToDisk(_, target, source, env):
    assert "UPLOAD_PORT" in env
    progname = env.subst("$PROGNAME")
    for ext in ("bin", "hex"):
        fpath = join(env.subst("$BUILD_DIR"), "%s.%s" % (progname, ext))
        if not isfile(fpath):
            continue
        copyfile(fpath, join(env.subst("$UPLOAD_PORT"), "%s.%s" % (progname, ext)))
    print(
        "Firmware has been successfully uploaded.\n"
        "(Some boards may require manual hard reset)"
    )


def CheckUploadSize(_, target, source, env):
    check_conditions = [
        env.get("BOARD"),
        env.get("SIZETOOL") or env.get("SIZECHECKCMD"),
    ]
    if not all(check_conditions):
        return
    program_max_size = int(env.BoardConfig().get("upload.maximum_size", 0))
    data_max_size = int(env.BoardConfig().get("upload.maximum_ram_size", 0))
    if program_max_size == 0:
        return

    def _configure_defaults():
        env.Replace(
            SIZECHECKCMD="$SIZETOOL -B -d $SOURCES",
            SIZEPROGREGEXP=r"^(\d+)\s+(\d+)\s+\d+\s",
            SIZEDATAREGEXP=r"^\d+\s+(\d+)\s+(\d+)\s+\d+",
        )

    def _get_size_output():
        cmd = env.get("SIZECHECKCMD")
        if not cmd:
            return None
        if not isinstance(cmd, list):
            cmd = cmd.split()
        cmd = [arg.replace("$SOURCES", str(source[0])) for arg in cmd if arg]
        sysenv = environ.copy()
        sysenv["PATH"] = str(env["ENV"]["PATH"])
        result = exec_command(env.subst(cmd), env=sysenv)
        if result["returncode"] != 0:
            return None
        return result["out"].strip()

    def _calculate_size(output, pattern):
        if not output or not pattern:
            return -1
        size = 0
        regexp = re.compile(pattern)
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            match = regexp.search(line)
            if not match:
                continue
            size += sum(int(value) for value in match.groups())
        return size

    def _format_availale_bytes(value, total):
        percent_raw = float(value) / float(total)
        blocks_per_progress = 10
        used_blocks = int(round(blocks_per_progress * percent_raw))
        if used_blocks > blocks_per_progress:
            used_blocks = blocks_per_progress
        return "[{:{}}] {: 6.1%} (used {:d} bytes from {:d} bytes)".format(
            "=" * used_blocks, blocks_per_progress, percent_raw, value, total
        )

    if not env.get("SIZECHECKCMD") and not env.get("SIZEPROGREGEXP"):
        _configure_defaults()
    output = _get_size_output()
    program_size = _calculate_size(output, env.get("SIZEPROGREGEXP"))
    data_size = _calculate_size(output, env.get("SIZEDATAREGEXP"))

    print('Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"')
    if data_max_size and data_size > -1:
        print("RAM:   %s" % _format_availale_bytes(data_size, data_max_size))
    if program_size > -1:
        print("Flash: %s" % _format_availale_bytes(program_size, program_max_size))
    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        print(output)

    # raise error
    # if data_max_size and data_size > data_max_size:
    #     sys.stderr.write(
    #         "Error: The data size (%d bytes) is greater "
    #         "than maximum allowed (%s bytes)\n" % (data_size, data_max_size))
    #     env.Exit(1)
    if program_size > program_max_size:
        sys.stderr.write(
            "Error: The program size (%d bytes) is greater "
            "than maximum allowed (%s bytes)\n" % (program_size, program_max_size)
        )
        env.Exit(1)


def PrintUploadInfo(env):
    configured = env.subst("$UPLOAD_PROTOCOL")
    available = [configured] if configured else []
    if "BOARD" in env:
        available.extend(env.BoardConfig().get("upload", {}).get("protocols", []))
    if available:
        print("AVAILABLE: %s" % ", ".join(sorted(set(available))))
    if configured:
        print("CURRENT: upload_protocol = %s" % configured)


def exists(_):
    return True


def generate(env):
    env.AddMethod(FlushSerialBuffer)
    env.AddMethod(TouchSerialPort)
    env.AddMethod(WaitForNewSerialPort)
    env.AddMethod(AutodetectUploadPort)
    env.AddMethod(UploadToDisk)
    env.AddMethod(CheckUploadSize)
    env.AddMethod(PrintUploadInfo)
    return env
