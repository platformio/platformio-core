# Copyright 2014-present Ivan Kravets <me@ikravets.com>
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

import base64
import json
import sys
from os import environ
from os.path import join, normpath
from time import time

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment, Variables

from platformio import util

# AllowSubstExceptions()

# allow common variables from INI file
commonvars = Variables(None)
commonvars.AddVariables(
    ("PLATFORM_MANIFEST",),
    ("BUILD_SCRIPT",),
    ("EXTRA_SCRIPT",),
    ("PIOENV",),
    ("PLATFORM",),

    # options
    ("FRAMEWORK",),
    ("BUILD_FLAGS",),
    ("SRC_BUILD_FLAGS",),
    ("BUILD_UNFLAGS",),
    ("SRC_FILTER",),
    ("LIB_DFCYCLIC",),
    ("LIB_IGNORE",),
    ("LIB_USE",),

    # board options
    ("BOARD",),
    ("BOARD_MCU",),
    ("BOARD_F_CPU",),
    ("BOARD_F_FLASH",),
    ("BOARD_FLASH_MODE",),

    # upload options
    ("UPLOAD_PORT",),
    ("UPLOAD_PROTOCOL",),
    ("UPLOAD_SPEED",),
    ("UPLOAD_FLAGS",),
    ("UPLOAD_RESETMETHOD",)
)

DefaultEnvironment(
    tools=[
        "gcc", "g++", "as", "ar", "gnulink",
        "platformio", "devplatform", "pioupload", "pioar", "piomisc"
    ],
    toolpath=[join(util.get_source_dir(), "builder", "tools")],
    variables=commonvars,

    # Propagating External Environment
    ENV=environ,

    UNIX_TIME=int(time()),
    PROGNAME="program",

    PIOHOME_DIR=util.get_home_dir(),
    PROJECT_DIR=util.get_project_dir(),
    PROJECTLIB_DIR=util.get_projectlib_dir(),
    PROJECTSRC_DIR=util.get_projectsrc_dir(),
    PROJECTDATA_DIR=util.get_projectdata_dir(),
    PIOENVS_DIR=util.get_pioenvs_dir(),

    BUILD_DIR=join("$PIOENVS_DIR", "$PIOENV"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src"),
    LIBSOURCE_DIRS=[
        "$PROJECTLIB_DIR",
        util.get_lib_dir()
    ],

    PYTHONEXE=normpath(sys.executable)
)

env = DefaultEnvironment()

# decode common variables
for k in commonvars.keys():
    if k in env:
        env[k] = base64.b64decode(env[k])

env.LoadDevPlatform(commonvars)

# Parse library names
for opt in ("LIB_IGNORE", "LIB_USE"):
    if opt not in env:
        continue
    env[opt] = [l.strip() for l in env[opt].split(",") if l.strip()]

# Handle custom variables from system environment
for var in ("BUILD_FLAGS", "SRC_BUILD_FLAGS", "SRC_FILTER", "EXTRA_SCRIPT",
            "UPLOAD_PORT", "UPLOAD_FLAGS"):
    k = "PLATFORMIO_%s" % var
    if environ.get(k):
        env[var] = environ.get(k)


env.SConscriptChdir(0)
env.SConsignFile(join("$PIOENVS_DIR", ".sconsign.dblite"))
env.SConscript("$BUILD_SCRIPT")


if "UPLOAD_FLAGS" in env:
    env.Append(UPLOADERFLAGS=["$UPLOAD_FLAGS"])

if env.get("EXTRA_SCRIPT"):
    env.SConscript(env.get("EXTRA_SCRIPT"))

if "envdump" in COMMAND_LINE_TARGETS:
    print env.Dump()
    env.Exit()

if "idedata" in COMMAND_LINE_TARGETS:
    print json.dumps(env.DumpIDEData())
    env.Exit()
