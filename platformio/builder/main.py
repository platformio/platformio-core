# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

from os import environ, makedirs
from os.path import isdir, join
from time import time

import click
from SCons.Script import ARGUMENTS  # pylint: disable=import-error
from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error
from SCons.Script import DEFAULT_TARGETS  # pylint: disable=import-error
from SCons.Script import AllowSubstExceptions  # pylint: disable=import-error
from SCons.Script import AlwaysBuild  # pylint: disable=import-error
from SCons.Script import Default  # pylint: disable=import-error
from SCons.Script import DefaultEnvironment  # pylint: disable=import-error
from SCons.Script import Import  # pylint: disable=import-error
from SCons.Script import Variables  # pylint: disable=import-error

from platformio import util
from platformio.compat import PY2, dump_json_to_unicode
from platformio.managers.platform import PlatformBase
from platformio.proc import get_pythonexe_path
from platformio.project import helpers as project_helpers

AllowSubstExceptions(NameError)

# append CLI arguments to build environment
clivars = Variables(None)
clivars.AddVariables(
    ("PLATFORM_MANIFEST",),
    ("BUILD_SCRIPT",),
    ("PROJECT_CONFIG",),
    ("PIOENV",),
    ("PIOTEST_RUNNING_NAME",),
    ("UPLOAD_PORT",)
)  # yapf: disable

DEFAULT_ENV_OPTIONS = dict(
    tools=[
        "ar", "gas", "gcc", "g++", "gnulink", "platformio", "pioplatform",
        "pioproject", "piowinhooks", "piolib", "pioupload", "piomisc", "pioide"
    ],
    toolpath=[join(util.get_source_dir(), "builder", "tools")],
    variables=clivars,

    # Propagating External Environment
    ENV=environ,
    UNIX_TIME=int(time()),
    PROJECT_DIR=project_helpers.get_project_dir(),
    PROJECTCORE_DIR=project_helpers.get_project_core_dir(),
    PROJECTPACKAGES_DIR=project_helpers.get_project_packages_dir(),
    PROJECTWORKSPACE_DIR=project_helpers.get_project_workspace_dir(),
    PROJECTLIBDEPS_DIR=project_helpers.get_project_libdeps_dir(),
    PROJECTINCLUDE_DIR=project_helpers.get_project_include_dir(),
    PROJECTSRC_DIR=project_helpers.get_project_src_dir(),
    PROJECTTEST_DIR=project_helpers.get_project_test_dir(),
    PROJECTDATA_DIR=project_helpers.get_project_data_dir(),
    PROJECTBUILD_DIR=project_helpers.get_project_build_dir(),
    BUILDCACHE_DIR=project_helpers.get_project_optional_dir("build_cache_dir"),
    BUILD_DIR=join("$PROJECTBUILD_DIR", "$PIOENV"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src"),
    BUILDTEST_DIR=join("$BUILD_DIR", "test"),
    LIBPATH=["$BUILD_DIR"],
    LIBSOURCE_DIRS=[
        project_helpers.get_project_lib_dir(),
        join("$PROJECTLIBDEPS_DIR", "$PIOENV"),
        project_helpers.get_project_global_lib_dir()
    ],
    PROGNAME="program",
    PROG_PATH=join("$BUILD_DIR", "$PROGNAME$PROGSUFFIX"),
    PYTHONEXE=get_pythonexe_path())

if not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    DEFAULT_ENV_OPTIONS['ARCOMSTR'] = "Archiving $TARGET"
    DEFAULT_ENV_OPTIONS['LINKCOMSTR'] = "Linking $TARGET"
    DEFAULT_ENV_OPTIONS['RANLIBCOMSTR'] = "Indexing $TARGET"
    for k in ("ASCOMSTR", "ASPPCOMSTR", "CCCOMSTR", "CXXCOMSTR"):
        DEFAULT_ENV_OPTIONS[k] = "Compiling $TARGET"

env = DefaultEnvironment(**DEFAULT_ENV_OPTIONS)

# Load variables from CLI
env.Replace(
    **{
        key: PlatformBase.decode_scons_arg(env[key])
        for key in list(clivars.keys()) if key in env
    })

if env.subst("$BUILDCACHE_DIR"):
    if not isdir(env.subst("$BUILDCACHE_DIR")):
        makedirs(env.subst("$BUILDCACHE_DIR"))
    env.CacheDir("$BUILDCACHE_DIR")

if int(ARGUMENTS.get("ISATTY", 0)):
    # pylint: disable=protected-access
    click._compat.isatty = lambda stream: True

if env.GetOption('clean'):
    env.PioClean(env.subst("$BUILD_DIR"))
    env.Exit(0)
elif not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    print("Verbose mode can be enabled via `-v, --verbose` option")

env.LoadProjectOptions()
env.LoadPioPlatform()

env.SConscriptChdir(0)
env.SConsignFile(
    join("$PROJECTBUILD_DIR",
         ".sconsign.dblite" if PY2 else ".sconsign3.dblite"))

for item in env.GetExtraScripts("pre"):
    env.SConscript(item, exports="env")

env.SConscript("$BUILD_SCRIPT")

if "UPLOAD_FLAGS" in env:
    env.Prepend(UPLOADERFLAGS=["$UPLOAD_FLAGS"])
if env.GetProjectOption("upload_command"):
    env.Replace(UPLOADCMD=env.GetProjectOption("upload_command"))

for item in env.GetExtraScripts("post"):
    env.SConscript(item, exports="env")

##############################################################################

# Checking program size
if env.get("SIZETOOL") and "nobuild" not in COMMAND_LINE_TARGETS:
    env.Depends(["upload", "program"], "checkprogsize")
    # Replace platform's "size" target with our
    _new_targets = [t for t in DEFAULT_TARGETS if str(t) != "size"]
    Default(None)
    Default(_new_targets)
    Default("checkprogsize")

# Print configured protocols
env.AddPreAction(
    ["upload", "program"],
    env.VerboseAction(lambda source, target, env: env.PrintUploadInfo(),
                      "Configuring upload protocol..."))

AlwaysBuild(env.Alias("debug", DEFAULT_TARGETS))
AlwaysBuild(env.Alias("__test", DEFAULT_TARGETS))

##############################################################################

if "envdump" in COMMAND_LINE_TARGETS:
    print(env.Dump())
    env.Exit(0)

if "idedata" in COMMAND_LINE_TARGETS:
    Import("projenv")
    print("\n%s\n" % dump_json_to_unicode(
        env.DumpIDEData(projenv)  # pylint: disable=undefined-variable
    ))
    env.Exit(0)
