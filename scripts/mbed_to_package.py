# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import argparse
import zipfile
from os import getcwd, listdir, makedirs, mkdir, rename
from os.path import isdir, isfile, join
from shutil import move, rmtree
from sys import exit as sys_exit
from sys import path

path.append("..")

from platformio.util import exec_command


def _unzip_generated_file(mbed_dir, output_dir, mcu):
    filename = join(
        mbed_dir, "build", "export", "MBED_A1_emblocks_%s.zip" % mcu)
    variant_dir = join(output_dir, "variant", mcu)
    if isfile(filename):
        print "Processing board: %s" % mcu
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


def main(mbed_dir, output_dir):
    print "Starting..."

    path.append(mbed_dir)
    from workspace_tools.export import gccarm

    if isdir(output_dir):
        print "Deleting previous framework dir..."
        rmtree(output_dir)

    makedirs(join(output_dir, "variant"))
    # make .eix files
    for mcu in set(gccarm.GccArm.TARGETS):
        exec_command(
            ["python", join(mbed_dir, "workspace_tools", "build.py"),
             "--mcu", mcu, "-t", "GCC_ARM"], cwd=getcwd()
        )
        exec_command(
            ["python", join(mbed_dir, "workspace_tools", "project.py"),
             "--mcu", mcu, "-i", "emblocks", "-p", "0", "-b"], cwd=getcwd()
        )
        _unzip_generated_file(mbed_dir, output_dir, mcu)
    print "Complete!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mbed', help="The path to mbed framework")
    parser.add_argument('--output', help="The path to output directory")
    args = vars(parser.parse_args())
    sys_exit(main(args["mbed"], args["output"]))
