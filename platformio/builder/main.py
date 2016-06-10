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

import base64
import json
import sys
from os import environ
from os.path import join, normpath
from time import time

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment, Variables

from platformio import util
from platformio.exception import UnknownBoard

# AllowSubstExceptions()

# allow common variables from INI file
commonvars = Variables(None)
commonvars.AddVariables(
    ("BUILD_SCRIPT",),
    ("EXTRA_SCRIPT",),
    ("PIOENV",),
    ("PLATFORM",),

    # package aliases
    ("PIOPACKAGE_TOOLCHAIN",),
    ("PIOPACKAGE_FRAMEWORK",),
    ("PIOPACKAGE_UPLOADER",),

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
        "platformio", "pioupload", "pioar", "piomisc"
    ],
    toolpath=[join("$PIOBUILDER_DIR", "tools")],
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

    PIOBUILDER_DIR=join(util.get_source_dir(), "builder"),
    PIOPACKAGES_DIR=join("$PIOHOME_DIR", "packages"),

    BUILD_DIR=join("$PIOENVS_DIR", "$PIOENV"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src"),
    LIBSOURCE_DIRS=[
        "$PROJECTLIB_DIR",
        util.get_lib_dir(),
        join("$PLATFORMFW_DIR", "libraries")
    ],

    PYTHONEXE=normpath(sys.executable)
)

env = DefaultEnvironment()

# decode common variables
for k in commonvars.keys():
    if k in env:
        env[k] = base64.b64decode(env[k])

env.Prepend(LIBPATH=[join("$PIOPACKAGES_DIR", "ldscripts")])

if "BOARD" in env:
    try:
        env.Replace(BOARD_OPTIONS=util.get_boards(env.subst("$BOARD")))
    except UnknownBoard as e:
        env.Exit("Error: %s" % str(e))

    for k in commonvars.keys():
        if (k in env or
                not any([k.startswith("BOARD_"), k.startswith("UPLOAD_")])):
            continue
        _opt, _val = k.lower().split("_", 1)
        if _opt == "board":
            _opt = "build"
        if _val in env['BOARD_OPTIONS'][_opt]:
            env.Replace(**{k: "${BOARD_OPTIONS['%s']['%s']}" % (_opt, _val)})

    if "ldscript" in env.get("BOARD_OPTIONS", {}).get("build", {}):
        env.Replace(
            LDSCRIPT_PATH="${BOARD_OPTIONS['build']['ldscript']}"
        )

    if env['PLATFORM'] != env.get("BOARD_OPTIONS", {}).get("platform"):
        env.Exit(
            "Error: '%s' platform doesn't support this board. "
            "Use '%s' platform instead." % (
                env['PLATFORM'], env.get("BOARD_OPTIONS", {}).get("platform")))


for opt in ("LIB_IGNORE", "LIB_USE"):
    if opt not in env:
        continue
    env[opt] = [l.strip() for l in env[opt].split(",") if l.strip()]

if env.subst("$PIOPACKAGE_TOOLCHAIN"):
    env.PrependENVPath(
        "PATH",
        env.subst(join("$PIOPACKAGES_DIR", "$PIOPACKAGE_TOOLCHAIN", "bin"))
    )

# handle custom variable from system environment
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
