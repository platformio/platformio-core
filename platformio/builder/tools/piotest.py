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

import atexit
from os import remove
from os.path import isdir, isfile, join, sep
from string import Template

FRAMEWORK_PARAMETERS = {
    "arduino": {
        "framework": "Arduino.h",
        "serial_obj": "",
        "serial_putc": "Serial.write(a)",
        "serial_flush": "Serial.flush()",
        "serial_begin": "Serial.begin(9600)",
        "serial_end": "Serial.end()"
    },

    "mbed": {
        "framework": "mbed.h",
        "serial_obj": "Serial pc(USBTX, USBRX);",
        "serial_putc": "pc.putc(a)",
        "serial_flush": "",
        "serial_begin": "pc.baud(9600)",
        "serial_end": ""
    },

    "energia": {
        "framework": "Energia.h",
        "serial_obj": "",
        "serial_putc": "Serial.write(a)",
        "serial_flush": "Serial.flush()",
        "serial_begin": "Serial.begin(9600)",
        "serial_end": "Serial.end()"
    }
}


def ProcessTest(env):
    env.Append(
        CPPDEFINES=[
            "UNIT_TEST",
            "UNITY_INCLUDE_CONFIG_H"
        ],

        CPPPATH=[
            join("$BUILD_DIR", "UnityTestLib")
        ]
    )
    unitylib = env.BuildLibrary(
        join("$BUILD_DIR", "UnityTestLib"),
        env.PioPlatform().get_package_dir("tool-unity")

    )
    env.Prepend(LIBS=[unitylib])

    test_dir = env.subst("$PROJECTTEST_DIR")
    env.GenerateOutputReplacement(test_dir)
    src_filter = None
    if "PIOTEST" in env:
        src_filter = "+<output_export.cpp>"
        src_filter += " +<%s%s>" % (env['PIOTEST'], sep)

    return env.CollectBuildFiles(
        "$BUILDTEST_DIR", test_dir, src_filter=src_filter, duplicate=False
    )


def GenerateOutputReplacement(env, destination_dir):

    if not isdir(env.subst(destination_dir)):
        env.Exit(
            "Error: Test folder doesn't exist. Please put your test suite "
            'to \"test\" folder in project\'s root directory.')

    TEMPLATECPP = """
# include <$framework>
# include <output_export.h>

$serial_obj

void output_char(int a)
{
    $serial_putc;
}

void output_flush(void)
{
    $serial_flush;
}

void output_start(unsigned int baudrate)
{
    $serial_begin;
}

void output_complete(void)
{
   $serial_end;
}

"""

    def delete_tmptest_file(file_):
        try:
            remove(file_)
        except:  # pylint: disable=bare-except
            if isfile(file_):
                print("Warning: Could not remove temporary file '%s'. "
                      "Please remove it manually." % file_)

    framework = env.subst("$PIOFRAMEWORK").lower()
    if framework not in FRAMEWORK_PARAMETERS:
        env.Exit(
            "Error: %s framework doesn't support testing feature!" % framework)
    else:
        data = Template(TEMPLATECPP).substitute(
            FRAMEWORK_PARAMETERS[framework])

        tmp_file = join(destination_dir, "output_export.cpp")
        with open(tmp_file, "w") as f:
            f.write(data)

        atexit.register(delete_tmptest_file, tmp_file)


def exists(_):
    return True


def generate(env):
    env.AddMethod(ProcessTest)
    env.AddMethod(GenerateOutputReplacement)
    return env
