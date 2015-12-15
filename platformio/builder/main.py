# Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
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

# pylint: disable=wrong-import-position,wrong-import-order,unused-import

try:
    from platformio import util
except ImportError:
    import sys
    for p in sys.path:
        _new_paths = []
        for item in ("dist-packages", "site-packages"):
            if not p.endswith(item) and item in p:
                _new_paths.append(p[:p.rfind(item) + len(item)])
        if "platformio" in p:
            _new_paths.append(p[:p.rfind("platformio") - 1])

        for _p in _new_paths:
            if _p not in sys.path:
                sys.path.insert(0, _p)
        try:
            from platformio import util
            import lockfile  # NOQA
            break
        except ImportError:
            pass

import json
from os import environ
from os.path import isfile, join
from time import time

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment, Variables

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
    ("SRC_FILTER",),
    ("LIB_DFCYCLIC",),
    ("LIB_IGNORE",),
    ("LIB_USE",),

    # board options
    ("BOARD",),
    ("BOARD_MCU",),
    ("BOARD_F_CPU",),

    # upload options
    ("UPLOAD_PORT",),
    ("UPLOAD_PROTOCOL",),
    ("UPLOAD_SPEED",),
    ("UPLOAD_FLAGS",)
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
    PIOENVS_DIR=util.get_pioenvs_dir(),

    PIOBUILDER_DIR=join(util.get_source_dir(), "builder"),
    PIOPACKAGES_DIR=join("$PIOHOME_DIR", "packages"),

    BUILD_DIR=join("$PIOENVS_DIR", "$PIOENV"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src"),
    LIBSOURCE_DIRS=[
        "$PROJECTLIB_DIR",
        util.get_lib_dir(),
        join("$PLATFORMFW_DIR", "libraries")
    ]
)

env = DefaultEnvironment()

if "BOARD" in env:
    try:
        env.Replace(BOARD_OPTIONS=util.get_boards(env.subst("$BOARD")))
    except UnknownBoard as e:
        env.Exit("Error: %s" % str(e))

    if "BOARD_MCU" not in env:
        env.Replace(BOARD_MCU="${BOARD_OPTIONS['build']['mcu']}")
    if "BOARD_F_CPU" not in env:
        env.Replace(BOARD_F_CPU="${BOARD_OPTIONS['build']['f_cpu']}")
    if "UPLOAD_PROTOCOL" not in env:
        env.Replace(
            UPLOAD_PROTOCOL="${BOARD_OPTIONS['upload'].get('protocol', None)}")
    if "UPLOAD_SPEED" not in env:
        env.Replace(
            UPLOAD_SPEED="${BOARD_OPTIONS['upload'].get('speed', None)}")
    if "ldscript" in env.get("BOARD_OPTIONS", {}).get("build", {}):
        env.Replace(
            LDSCRIPT_PATH=(
                env['BOARD_OPTIONS']['build']['ldscript']
                if isfile(env['BOARD_OPTIONS']['build']['ldscript'])
                else join("$PIOHOME_DIR", "packages", "ldscripts",
                          "${BOARD_OPTIONS['build']['ldscript']}")
            )
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

env.SConscriptChdir(0)
env.SConsignFile(join("$PIOENVS_DIR", ".sconsign.dblite"))
env.SConscript("$BUILD_SCRIPT")

if "UPLOAD_FLAGS" in env:
    env.Append(UPLOADERFLAGS=["$UPLOAD_FLAGS"])

if environ.get("PLATFORMIO_EXTRA_SCRIPT", env.get("EXTRA_SCRIPT")):
    env.SConscript(
        environ.get("PLATFORMIO_EXTRA_SCRIPT", env.get("EXTRA_SCRIPT")))

if "envdump" in COMMAND_LINE_TARGETS:
    print env.Dump()
    env.Exit()

if "idedata" in COMMAND_LINE_TARGETS:
    print json.dumps(env.DumpIDEData())
    env.Exit()
