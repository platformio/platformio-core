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

from os.path import isfile, join
from shutil import copyfile
from time import sleep

from serial import Serial

from platformio.util import get_logicaldisks, get_serialports, get_systype


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
    if "windows" not in get_systype():
        try:
            s = Serial(env.subst(port))
            s.close()
        except:  # pylint: disable=W0702
            pass
    s = Serial(port=env.subst(port), baudrate=baudrate)
    s.setDTR(False)
    s.close()
    sleep(0.4)


def WaitForNewSerialPort(env, before):
    print "Waiting for the new upload port..."
    prev_port = env.subst("$UPLOAD_PORT")
    new_port = None
    elapsed = 0
    while elapsed < 5 and new_port is None:
        now = get_serialports()
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


def AutodetectUploadPort(env):
    if "UPLOAD_PORT" in env:
        return

    if env.subst("$FRAMEWORK") == "mbed":
        msdlabels = ("mbed", "nucleo", "frdm")
        for item in get_logicaldisks():
            if (not item['name'] or
                    not any([l in item['name'].lower() for l in msdlabels])):
                continue
            env.Replace(UPLOAD_PORT=item['disk'])
            break
    else:
        if not isfile("/etc/udev/99-platformio-udev.rules"):
            print (
                "\nWarning! Please install `99-platformio-udev.rules` and "
                "check that your board's PID and VID are listed in the rules."
                "\n https://raw.githubusercontent.com/platformio/platformio"
                "/develop/scripts/99-platformio-udev.rules\n"
            )

        board_build_opts = env.get("BOARD_OPTIONS", {}).get("build", {})
        for item in get_serialports():
            if "VID:PID" not in item['hwid']:
                continue
            env.Replace(UPLOAD_PORT=item['port'])
            for hwid in board_build_opts.get("hwid", []):
                board_hwid = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if board_hwid in item['hwid']:
                    break

    if "UPLOAD_PORT" in env:
        print "Auto-detected UPLOAD_PORT/DISK: %s" % env['UPLOAD_PORT']
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


def exists(_):
    return True


def generate(env):
    env.AddMethod(FlushSerialBuffer)
    env.AddMethod(TouchSerialPort)
    env.AddMethod(WaitForNewSerialPort)
    env.AddMethod(AutodetectUploadPort)
    env.AddMethod(UploadToDisk)
    return env
