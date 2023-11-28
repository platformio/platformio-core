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

# pylint: disable=unused-argument

import os
import re
import sys
from shutil import copyfile
from time import sleep

from SCons.Script import ARGUMENTS  # pylint: disable=import-error
from serial import Serial, SerialException

from platformio import exception, fs
from platformio.device.finder import SerialPortFinder, find_mbed_disk, is_pattern_port
from platformio.device.list.util import list_serial_ports
from platformio.proc import exec_command


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
        now = [p["port"] for p in list_serial_ports()]
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
    initial_port = env.subst("$UPLOAD_PORT")
    upload_protocol = env.subst("$UPLOAD_PROTOCOL")
    if initial_port and not is_pattern_port(initial_port):
        print(env.subst("Using manually specified: $UPLOAD_PORT"))
        return

    if upload_protocol == "mbed" or (
        "mbed" in env.subst("$PIOFRAMEWORK") and not upload_protocol
    ):
        env.Replace(UPLOAD_PORT=find_mbed_disk(initial_port))
    else:
        try:
            fs.ensure_udev_rules()
        except exception.InvalidUdevRules as exc:
            sys.stderr.write("\n%s\n\n" % exc)
        env.Replace(
            UPLOAD_PORT=SerialPortFinder(
                board_config=env.BoardConfig() if "BOARD" in env else None,
                upload_protocol=upload_protocol,
                prefer_gdb_port="blackmagic" in upload_protocol,
                verbose=int(ARGUMENTS.get("PIOVERBOSE", 0)),
            ).find(initial_port)
        )

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
        fpath = os.path.join(env.subst("$BUILD_DIR"), "%s.%s" % (progname, ext))
        if not os.path.isfile(fpath):
            continue
        copyfile(
            fpath, os.path.join(env.subst("$UPLOAD_PORT"), "%s.%s" % (progname, ext))
        )
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
        sysenv = os.environ.copy()
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
        used_blocks = min(
            int(round(blocks_per_progress * percent_raw)), blocks_per_progress
        )
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

    if data_max_size and data_size > data_max_size:
        sys.stderr.write(
            "Warning! The data size (%d bytes) is greater "
            "than maximum allowed (%s bytes)\n" % (data_size, data_max_size)
        )
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
