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

import sys
from fnmatch import fnmatch
from os import environ
from os.path import isfile, join
from platform import system
from shutil import copyfile
from time import sleep

from SCons.Node.Alias import Alias
from serial import Serial, SerialException

from platformio import util


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
    print "Forcing reset using %dbps open/close on port %s" % (baudrate, port)
    try:
        s = Serial(port=port, baudrate=baudrate)
        s.setDTR(False)
        s.close()
    except:  # pylint: disable=W0702
        pass


def WaitForNewSerialPort(env, before):
    print "Waiting for the new upload port..."
    prev_port = env.subst("$UPLOAD_PORT")
    new_port = None
    elapsed = 0
    before = [p['port'] for p in before]
    while elapsed < 5 and new_port is None:
        now = [p['port'] for p in util.get_serialports()]
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
        sys.stderr.write("Error: Couldn't find a board on the selected port. "
                         "Check that you have the correct port selected. "
                         "If it is correct, try pressing the board's reset "
                         "button after initiating the upload.\n")
        env.Exit(1)

    return new_port


def AutodetectUploadPort(*args, **kwargs):  # pylint: disable=unused-argument
    env = args[0]

    def _get_pattern():
        if "UPLOAD_PORT" not in env:
            return None
        if set(["*", "?", "[", "]"]) & set(env['UPLOAD_PORT']):
            return env['UPLOAD_PORT']
        return None

    def _is_match_pattern(port):
        pattern = _get_pattern()
        if not pattern:
            return True
        return fnmatch(port, pattern)

    def _look_for_mbed_disk():
        msdlabels = ("mbed", "nucleo", "frdm", "microbit")
        for item in util.get_logicaldisks():
            if item['disk'].startswith(
                    "/net") or not _is_match_pattern(item['disk']):
                continue
            mbed_pages = [
                join(item['disk'], n) for n in ("mbed.htm", "mbed.html")
            ]
            if any([isfile(p) for p in mbed_pages]):
                return item['disk']
            if (item['name'] and
                    any([l in item['name'].lower() for l in msdlabels])):
                return item['disk']
        return None

    def _look_for_serial_port():
        port = None
        board_hwids = []
        if "BOARD" in env and "build.hwids" in env.BoardConfig():
            board_hwids = env.BoardConfig().get("build.hwids")
        for item in util.get_serialports(filter_hwid=True):
            if not _is_match_pattern(item['port']):
                continue
            port = item['port']
            for hwid in board_hwids:
                hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if hwid_str in item['hwid']:
                    return port
        return port

    if "UPLOAD_PORT" in env and not _get_pattern():
        print env.subst("Use manually specified: $UPLOAD_PORT")
        return

    if "mbed" in env.subst("$PIOFRAMEWORK"):
        env.Replace(UPLOAD_PORT=_look_for_mbed_disk())
    else:
        if (system() == "Linux" and not any([
                isfile("/etc/udev/rules.d/99-platformio-udev.rules"),
                isfile("/lib/udev/rules.d/99-platformio-udev.rules")
        ])):
            sys.stderr.write(
                "\nWarning! Please install `99-platformio-udev.rules` and "
                "check that your board's PID and VID are listed in the rules."
                "\n https://raw.githubusercontent.com/platformio/platformio"
                "/develop/scripts/99-platformio-udev.rules\n")
        env.Replace(UPLOAD_PORT=_look_for_serial_port())

    if env.subst("$UPLOAD_PORT"):
        print env.subst("Auto-detected: $UPLOAD_PORT")
    else:
        sys.stderr.write(
            "Error: Please specify `upload_port` for environment or use "
            "global `--upload-port` option.\n"
            "For some development platforms it can be a USB flash "
            "drive (i.e. /media/<user>/<device name>)\n")
        env.Exit(1)


def UploadToDisk(_, target, source, env):  # pylint: disable=W0613,W0621
    assert "UPLOAD_PORT" in env
    progname = env.subst("$PROGNAME")
    for ext in ("bin", "hex"):
        fpath = join(env.subst("$BUILD_DIR"), "%s.%s" % (progname, ext))
        if not isfile(fpath):
            continue
        copyfile(fpath,
                 join(env.subst("$UPLOAD_PORT"), "%s.%s" % (progname, ext)))
    print "Firmware has been successfully uploaded.\n"\
          "(Some boards may require manual hard reset)"


def CheckUploadSize(_, target, source, env):  # pylint: disable=W0613,W0621
    if "BOARD" not in env:
        return
    max_size = int(env.BoardConfig().get("upload.maximum_size", 0))
    if max_size == 0 or "SIZETOOL" not in env:
        return

    sysenv = environ.copy()
    sysenv['PATH'] = str(env['ENV']['PATH'])
    cmd = [
        env.subst("$SIZETOOL"), "-B",
        str(source[0] if isinstance(target[0], Alias) else target[0])
    ]
    result = util.exec_command(cmd, env=sysenv)
    if result['returncode'] != 0:
        return
    print result['out'].strip()

    line = result['out'].strip().splitlines()[1]
    values = [v.strip() for v in line.split("\t")]
    used_size = int(values[0]) + int(values[1])

    if used_size > max_size:
        sys.stderr.write("Error: The program size (%d bytes) is greater "
                         "than maximum allowed (%s bytes)\n" % (used_size,
                                                                max_size))
        env.Exit(1)


def exists(_):
    return True


def generate(env):
    env.AddMethod(FlushSerialBuffer)
    env.AddMethod(TouchSerialPort)
    env.AddMethod(WaitForNewSerialPort)
    env.AddMethod(AutodetectUploadPort)
    env.AddMethod(UploadToDisk)
    env.AddMethod(CheckUploadSize)
    return env
