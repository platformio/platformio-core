# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import argparse
import zipfile
from os import getcwd, listdir, makedirs, mkdir, rename
from os.path import isdir, isfile, join
from shutil import move, rmtree
from sys import exit as sys_exit
from sys import path

path.append("..")

from platformio.util import exec_command, get_home_dir


def _unzip_generated_file(mbed_dir, output_dir, mcu):
    filename = join(
        mbed_dir, "build", "export", "MBED_A1_emblocks_%s.zip" % mcu)
    variant_dir = join(output_dir, "variant", mcu)
    if isfile(filename):
        with zipfile.ZipFile(filename) as zfile:
            mkdir(variant_dir)
            zfile.extractall(variant_dir)
            for f in listdir(join(variant_dir, "MBED_A1")):
                if not f.lower().startswith("mbed"):
                    continue
                move(join(variant_dir, "MBED_A1", f), variant_dir)
            rename(join(variant_dir, "MBED_A1.eix"),
                   join(variant_dir, "%s.eix" % mcu))
            rmtree(join(variant_dir, "MBED_A1"))
    else:
        print "Warning! Skipped board: %s" % mcu


def buildlib(mbed_dir, mcu, lib="mbed"):
    build_command = [
        "python",
        join(mbed_dir, "workspace_tools", "build.py"),
        "--mcu", mcu,
        "-t", "GCC_ARM"
    ]
    if lib is not "mbed":
        build_command.append(lib)
    build_result = exec_command(build_command, cwd=getcwd())
    if build_result['returncode'] != 0:
        print "*     %s doesn't support %s library!" % (mcu, lib)


def copylibs(mbed_dir, output_dir):
    libs = ["dsp", "fat", "net", "rtos", "usb", "usb_host"]
    libs_dir = join(output_dir, "libs")
    makedirs(libs_dir)

    print "Moving generated libraries to framework dir..."
    for lib in libs:
        if lib == "net":
            move(join(mbed_dir, "build", lib, "eth"), libs_dir)
            continue
        move(join(mbed_dir, "build", lib), libs_dir)


def main(mbed_dir, output_dir):
    print "Starting..."

    path.append(mbed_dir)
    from workspace_tools.export import gccarm

    if isdir(output_dir):
        print "Deleting previous framework dir..."
        rmtree(output_dir)

    settings_file = join(mbed_dir, "workspace_tools", "private_settings.py")
    if not isfile(settings_file):
        with open(settings_file, "w") as f:
            f.write("GCC_ARM_PATH = '%s'" %
                    join(get_home_dir(), "packages", "toolchain-gccarmnoneeabi",
                         "bin"))

    makedirs(join(output_dir, "variant"))
    mbed_libs = ["--rtos", "--dsp", "--fat", "--eth", "--usb", "--usb_host"]

    for mcu in set(gccarm.GccArm.TARGETS):
        print "Processing board: %s" % mcu
        buildlib(mbed_dir, mcu)
        for lib in mbed_libs:
            buildlib(mbed_dir, mcu, lib)
        result = exec_command(
            ["python", join(mbed_dir, "workspace_tools", "project.py"),
             "--mcu", mcu, "-i", "emblocks", "-p", "0", "-b"], cwd=getcwd()
        )
        if result['returncode'] != 0:
            print "Unable to build the project for %s" % mcu
            continue
        _unzip_generated_file(mbed_dir, output_dir, mcu)
    copylibs(mbed_dir, output_dir)

    with open(join(output_dir, "boards.txt"), "w") as fp:
        fp.write("\n".join(sorted(listdir(join(output_dir, "variant")))))

    print "Complete!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mbed', help="The path to mbed framework")
    parser.add_argument('--output', help="The path to output directory")
    args = vars(parser.parse_args())
    sys_exit(main(args["mbed"], args["output"]))
