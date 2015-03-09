# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, mkdir, makedirs, listdir
from os.path import isfile, isdir, join
from shutil import copy2, rmtree, copytree
from sys import exit as sys_exit
from sys import path
import zipfile


MBED_DIR = "/home/valeros/mbed-master"
OUTPUT_DIR = "/home/valeros/mbed-framework"
CORE_DIR = join(OUTPUT_DIR, "core")
VARIANT_DIR = join(OUTPUT_DIR, "variant")

path.append("..")
path.append(MBED_DIR)
from workspace_tools.export import gccarm
from platformio.util import exec_command


def _unzip_generated_file(mcu):
    filename = join(
        MBED_DIR, "build", "export", "MBED_A1_emblocks_%s.zip" % mcu)
    variant_dir = join(VARIANT_DIR, mcu)
    if isfile(filename):
        print "Processing board: %s" % mcu
        with zipfile.ZipFile(filename) as zfile:
            mkdir(variant_dir)
            file_data = zfile.read("MBED_A1/MBED_A1.eix")
            with open(join(variant_dir, "%s.eix" % mcu), "w") as f:
                f.write(file_data)
    else:
        print "Warning! Skipped board: %s" % mcu


def main():
    print "Starting..."
    if isdir(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)
        print "Delete previous framework dir"
    makedirs(VARIANT_DIR)
    # copy MBED library
    mbedlib_dir = join(MBED_DIR, "libraries", "mbed")
    for item in listdir(mbedlib_dir):
        src = join(mbedlib_dir, item)
        dst = join(CORE_DIR, item)
        if isdir(src):
            copytree(src, dst)
        else:
            copy2(src, dst)
    # make .eix files
    for mcu in set(gccarm.GccArm.TARGETS):
        exec_command(
            ["python", join(MBED_DIR, "workspace_tools", "project.py"),
             "--mcu", mcu, "-i", "emblocks", "-p", "0"], cwd=getcwd()
        )
        _unzip_generated_file(mcu)
    print "Complete!"


if __name__ == "__main__":
    sys_exit(main())
