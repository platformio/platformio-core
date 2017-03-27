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

import base64
import json
from os import environ
from os.path import join
from time import time

from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, DEFAULT_TARGETS,
                          AllowSubstExceptions, AlwaysBuild,
                          DefaultEnvironment, Variables)

from platformio import util

AllowSubstExceptions(NameError)

# allow common variables from INI file
commonvars = Variables(None)
commonvars.AddVariables(
    ("PLATFORM_MANIFEST",),
    ("BUILD_SCRIPT",),
    ("EXTRA_SCRIPT",),
    ("PIOENV",),
    ("PIOTEST",),
    ("PIOPLATFORM",),
    ("PIOFRAMEWORK",),

    # build options
    ("BUILD_FLAGS",),
    ("SRC_BUILD_FLAGS",),
    ("BUILD_UNFLAGS",),
    ("SRC_FILTER",),

    # library options
    ("LIB_LDF_MODE",),
    ("LIB_COMPAT_MODE",),
    ("LIB_DEPS",),
    ("LIB_IGNORE",),
    ("LIB_EXTRA_DIRS",),

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
)  # yapf: disable

DEFAULT_ENV_OPTIONS = dict(
    tools=[
        "ar", "as", "gcc", "g++", "gnulink", "platformio", "pioplatform",
        "piowinhooks", "piolib", "piotest", "pioupload", "piomisc"
    ],  # yapf: disable
    toolpath=[join(util.get_source_dir(), "builder", "tools")],
    variables=commonvars,

    # Propagating External Environment
    PIOVARIABLES=commonvars.keys(),
    ENV=environ,
    UNIX_TIME=int(time()),
    PROGNAME="program",
    PIOHOME_DIR=util.get_home_dir(),
    PROJECT_DIR=util.get_project_dir(),
    PROJECTSRC_DIR=util.get_projectsrc_dir(),
    PROJECTTEST_DIR=util.get_projecttest_dir(),
    PROJECTDATA_DIR=util.get_projectdata_dir(),
    PROJECTPIOENVS_DIR=util.get_projectpioenvs_dir(),
    BUILD_DIR=join("$PROJECTPIOENVS_DIR", "$PIOENV"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src"),
    BUILDTEST_DIR=join("$BUILD_DIR", "test"),
    LIBSOURCE_DIRS=[
        util.get_projectlib_dir(), util.get_projectlibdeps_dir(),
        join("$PIOHOME_DIR", "lib")
    ],
    PYTHONEXE=util.get_pythonexe_path())

if not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    DEFAULT_ENV_OPTIONS['ARCOMSTR'] = "Archiving $TARGET"
    DEFAULT_ENV_OPTIONS['LINKCOMSTR'] = "Linking $TARGET"
    DEFAULT_ENV_OPTIONS['RANLIBCOMSTR'] = "Indexing $TARGET"
    for k in ("ASCOMSTR", "ASPPCOMSTR", "CCCOMSTR", "CXXCOMSTR"):
        DEFAULT_ENV_OPTIONS[k] = "Compiling $TARGET"

env = DefaultEnvironment(**DEFAULT_ENV_OPTIONS)

# decode common variables
for k in commonvars.keys():
    if k in env:
        env[k] = base64.b64decode(env[k])

if env.GetOption('clean'):
    env.PioClean(env.subst("$BUILD_DIR"))
    env.Exit(0)
elif not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    print "Verbose mode can be enabled via `-v, --verbose` option"

# Handle custom variables from system environment
for var in ("BUILD_FLAGS", "SRC_BUILD_FLAGS", "SRC_FILTER", "EXTRA_SCRIPT",
            "UPLOAD_PORT", "UPLOAD_FLAGS", "LIB_EXTRA_DIRS"):
    k = "PLATFORMIO_%s" % var
    if k not in environ:
        continue
    if var in ("UPLOAD_PORT", "EXTRA_SCRIPT") or not env.get(var):
        env[var] = environ.get(k)
    else:
        env[var] = "%s%s%s" % (environ.get(k), ", "
                               if var == "LIB_EXTRA_DIRS" else " ", env[var])

# Parse comma separated items
for opt in ("PIOFRAMEWORK", "LIB_DEPS", "LIB_IGNORE", "LIB_EXTRA_DIRS"):
    if opt not in env:
        continue
    env[opt] = [l.strip() for l in env[opt].split(", ") if l.strip()]

# Configure extra library source directories for LDF
if util.get_project_optional_dir("lib_extra_dirs"):
    env.Prepend(LIBSOURCE_DIRS=[
        l.strip()
        for l in util.get_project_optional_dir("lib_extra_dirs").split(", ")
        if l.strip()
    ])
env.Prepend(LIBSOURCE_DIRS=env.get("LIB_EXTRA_DIRS", []))

env.LoadPioPlatform(commonvars)

env.SConscriptChdir(0)
env.SConsignFile(join("$PROJECTPIOENVS_DIR", ".sconsign.dblite"))
env.SConscript("$BUILD_SCRIPT")

AlwaysBuild(env.Alias("__test", DEFAULT_TARGETS + ["size"]))

if "UPLOAD_FLAGS" in env:
    env.Append(UPLOADERFLAGS=["$UPLOAD_FLAGS"])

if env.get("EXTRA_SCRIPT"):
    env.SConscript(env.get("EXTRA_SCRIPT"), exports="env")

if "envdump" in COMMAND_LINE_TARGETS:
    print env.Dump()
    env.Exit(0)

if "idedata" in COMMAND_LINE_TARGETS:
    print "\n%s\n" % json.dumps(env.DumpIDEData())
    env.Exit(0)
