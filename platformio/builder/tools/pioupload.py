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

from __future__ import absolute_import

from os import environ
from os.path import isfile, join
from platform import system
from shutil import copyfile
from time import sleep

from serial import Serial

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
    sleep(0.4)


def WaitForNewSerialPort(env, before):
    print "Waiting for the new upload port..."
    prev_port = env.subst("$UPLOAD_PORT")
    new_port = None
    elapsed = 0
    sleep(1)
    while elapsed < 5 and new_port is None:
        now = util.get_serialports()
        for p in now:
            if p not in before:
                new_port = p['port']
                break
        before = now
        sleep(0.25)
        elapsed += 0.25

    if not new_port:
        for p in now:
            if prev_port == p['port']:
                new_port = p['port']
                break

    if not new_port:
        env.Exit("Error: Couldn't find a board on the selected port. "
                 "Check that you have the correct port selected. "
                 "If it is correct, try pressing the board's reset "
                 "button after initiating the upload.")

    return new_port


def AutodetectUploadPort(*args, **kwargs):  # pylint: disable=unused-argument
    env = args[0]
    print "Looking for upload port/disk..."

    def _look_for_mbed_disk():
        msdlabels = ("mbed", "nucleo", "frdm")
        for item in util.get_logicaldisks():
            if (not item['name'] or
                    not any([l in item['name'].lower() for l in msdlabels])):
                continue
            return item['disk']
        return None

    def _look_for_serial_port():
        port = None
        board_hwids = env.get("BOARD_OPTIONS", {}).get(
            "build", {}).get("hwids", [])
        for item in util.get_serialports():
            if "VID:PID" not in item['hwid']:
                continue
            port = item['port']
            for hwid in board_hwids:
                hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if hwid_str in item['hwid']:
                    return port
        return port

    if "UPLOAD_PORT" in env:
        print env.subst("Manually specified: $UPLOAD_PORT")
        return

    if env.subst("$FRAMEWORK") == "mbed":
        env.Replace(UPLOAD_PORT=_look_for_mbed_disk())
    else:
        if (system() == "Linux" and
                not isfile("/etc/udev/99-platformio-udev.rules")):
            print(
                "\nWarning! Please install `99-platformio-udev.rules` and "
                "check that your board's PID and VID are listed in the rules."
                "\n https://raw.githubusercontent.com/platformio/platformio"
                "/develop/scripts/99-platformio-udev.rules\n"
            )
        env.Replace(UPLOAD_PORT=_look_for_serial_port())

    if env.subst("$UPLOAD_PORT"):
        print env.subst("Auto-detected: $UPLOAD_PORT")
    else:
        env.Exit("Error: Please specify `upload_port` for environment or use "
                 "global `--upload-port` option.\n"
                 "For some development platforms this can be a USB flash "
                 "drive (i.e. /media/<user>/<device name>)\n")


def UploadToDisk(_, target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()
    progname = env.subst("$PROGNAME")
    for ext in ("bin", "hex"):
        fpath = join(env.subst("$BUILD_DIR"), "%s.%s" % (progname, ext))
        if not isfile(fpath):
            continue
        copyfile(fpath, join(
            env.subst("$UPLOAD_PORT"), "%s.%s" % (progname, ext)))
    print("Firmware has been successfully uploaded.\n"
          "Please restart your board.")


def CheckUploadSize(_, target, source, env):  # pylint: disable=W0613,W0621
    max_size = int(env.get("BOARD_OPTIONS", {}).get("upload", {}).get(
        "maximum_size", 0))
    if max_size == 0 or "SIZETOOL" not in env:
        return

    print "Check program size..."
    sysenv = environ.copy()
    sysenv['PATH'] = str(env['ENV']['PATH'])
    cmd = [env.subst("$SIZETOOL"), "-B", str(target[0])]
    result = util.exec_command(cmd, env=sysenv)
    if result['returncode'] != 0:
        return
    print result['out'].strip()

    line = result['out'].strip().splitlines()[1]
    values = [v.strip() for v in line.split("\t")]
    used_size = int(values[0]) + int(values[1])

    if used_size > max_size:
        env.Exit("Error: The program size (%d bytes) is greater "
                 "than maximum allowed (%s bytes)" % (used_size, max_size))


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
