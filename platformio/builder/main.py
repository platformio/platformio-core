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

import json
import os
import sys
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

from platformio import app, compat, fs
from platformio.platform.base import PlatformBase
from platformio.proc import get_pythonexe_path
from platformio.project.helpers import get_project_dir

AllowSubstExceptions(NameError)

# append CLI arguments to build environment
clivars = Variables(None)
clivars.AddVariables(
    ("PLATFORM_MANIFEST",),
    ("BUILD_SCRIPT",),
    ("PROJECT_CONFIG",),
    ("PIOENV",),
    ("PIOTEST_RUNNING_NAME",),
    ("UPLOAD_PORT",),
    ("PROGRAM_ARGS",),
)

DEFAULT_ENV_OPTIONS = dict(
    tools=[
        "ar",
        "cc",
        "c++",
        "link",
        "piohooks",
        "pioasm",
        "piobuild",
        "pioproject",
        "pioplatform",
        "piotest",
        "piotarget",
        "piolib",
        "pioupload",
        "piosize",
        "pioino",
        "piomisc",
        "piointegration",
        "piomaxlen",
    ],
    toolpath=[os.path.join(fs.get_source_dir(), "builder", "tools")],
    variables=clivars,
    # Propagating External Environment
    ENV=os.environ,
    UNIX_TIME=int(time()),
    BUILD_DIR=os.path.join("$PROJECT_BUILD_DIR", "$PIOENV"),
    BUILD_SRC_DIR=os.path.join("$BUILD_DIR", "src"),
    BUILD_TEST_DIR=os.path.join("$BUILD_DIR", "test"),
    COMPILATIONDB_PATH=os.path.join("$PROJECT_DIR", "compile_commands.json"),
    LIBPATH=["$BUILD_DIR"],
    PROGNAME="program",
    PROGPATH=os.path.join("$BUILD_DIR", "$PROGNAME$PROGSUFFIX"),
    PROG_PATH="$PROGPATH",  # deprecated
    PYTHONEXE=get_pythonexe_path(),
)

# Declare command verbose messages
command_strings = dict(
    ARCOM="Archiving",
    LINKCOM="Linking",
    RANLIBCOM="Indexing",
    ASCOM="Compiling",
    ASPPCOM="Compiling",
    CCCOM="Compiling",
    CXXCOM="Compiling",
)
if not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    for name, value in command_strings.items():
        DEFAULT_ENV_OPTIONS["%sSTR" % name] = "%s $TARGET" % (value)

env = DefaultEnvironment(**DEFAULT_ENV_OPTIONS)

# Load variables from CLI
env.Replace(
    **{
        key: PlatformBase.decode_scons_arg(env[key])
        for key in list(clivars.keys())
        if key in env
    }
)

# Setup project optional directories
config = env.GetProjectConfig()
app.set_session_var("custom_project_conf", config.path)

env.Replace(
    PROJECT_DIR=get_project_dir(),
    PROJECT_CORE_DIR=config.get("platformio", "core_dir"),
    PROJECT_PACKAGES_DIR=config.get("platformio", "packages_dir"),
    PROJECT_WORKSPACE_DIR=config.get("platformio", "workspace_dir"),
    PROJECT_LIBDEPS_DIR=config.get("platformio", "libdeps_dir"),
    PROJECT_INCLUDE_DIR=config.get("platformio", "include_dir"),
    PROJECT_SRC_DIR=config.get("platformio", "src_dir"),
    PROJECTSRC_DIR="$PROJECT_SRC_DIR",  # legacy for dev/platform
    PROJECT_TEST_DIR=config.get("platformio", "test_dir"),
    PROJECT_DATA_DIR=config.get("platformio", "data_dir"),
    PROJECTDATA_DIR="$PROJECT_DATA_DIR",  # legacy for dev/platform
    PROJECT_BUILD_DIR=config.get("platformio", "build_dir"),
    BUILD_TYPE=env.GetBuildType(),
    BUILD_CACHE_DIR=config.get("platformio", "build_cache_dir"),
    LIBSOURCE_DIRS=[
        config.get("platformio", "lib_dir"),
        os.path.join("$PROJECT_LIBDEPS_DIR", "$PIOENV"),
        config.get("platformio", "globallib_dir"),
    ],
)

if int(ARGUMENTS.get("ISATTY", 0)):
    # pylint: disable=protected-access
    click._compat.isatty = lambda stream: True

if compat.IS_WINDOWS and sys.version_info >= (3, 8) and os.getcwd().startswith("\\\\"):
    click.secho("!!! WARNING !!!\t\t" * 3, fg="red")
    click.secho(
        "Your project is located on a mapped network drive but the "
        "current command-line shell does not support the UNC paths.",
        fg="yellow",
    )
    click.secho(
        "Please move your project to a physical drive or check this workaround: "
        "https://bit.ly/3kuU5mP\n",
        fg="yellow",
    )

if env.subst("$BUILD_CACHE_DIR"):
    if not os.path.isdir(env.subst("$BUILD_CACHE_DIR")):
        os.makedirs(env.subst("$BUILD_CACHE_DIR"))
    env.CacheDir("$BUILD_CACHE_DIR")

if not int(ARGUMENTS.get("PIOVERBOSE", 0)):
    click.echo("Verbose mode can be enabled via `-v, --verbose` option")

# Dynamically load dependent tools
if "compiledb" in COMMAND_LINE_TARGETS:
    env.Tool("compilation_db")

if not os.path.isdir(env.subst("$BUILD_DIR")):
    os.makedirs(env.subst("$BUILD_DIR"))

env.LoadProjectOptions()
env.LoadPioPlatform()

env.SConscriptChdir(0)
env.SConsignFile(
    os.path.join(
        "$BUILD_DIR", ".sconsign%d%d" % (sys.version_info[0], sys.version_info[1])
    )
)

for item in env.GetExtraScripts("pre"):
    env.SConscript(item, exports="env")

if env.IsCleanTarget():
    env.CleanProject("cleanall" in COMMAND_LINE_TARGETS)
    env.Exit(0)

env.SConscript("$BUILD_SCRIPT")

if "UPLOAD_FLAGS" in env:
    env.Prepend(UPLOADERFLAGS=["$UPLOAD_FLAGS"])
if env.GetProjectOption("upload_command"):
    env.Replace(UPLOADCMD=env.GetProjectOption("upload_command"))

for item in env.GetExtraScripts("post"):
    env.SConscript(item, exports="env")

##############################################################################

# Checking program size
if env.get("SIZETOOL") and not (
    set(["nobuild", "sizedata"]) & set(COMMAND_LINE_TARGETS)
):
    env.Depends("upload", "checkprogsize")
    # Replace platform's "size" target with our
    _new_targets = [t for t in DEFAULT_TARGETS if str(t) != "size"]
    Default(None)
    Default(_new_targets)
    Default("checkprogsize")

if "compiledb" in COMMAND_LINE_TARGETS:
    env.Alias("compiledb", env.CompilationDatabase("$COMPILATIONDB_PATH"))

# Print configured protocols
env.AddPreAction(
    "upload",
    env.VerboseAction(
        lambda source, target, env: env.PrintUploadInfo(),
        "Configuring upload protocol...",
    ),
)

AlwaysBuild(env.Alias("__debug", DEFAULT_TARGETS))
AlwaysBuild(env.Alias("__test", DEFAULT_TARGETS))

env.ProcessDelayedActions()

##############################################################################

if "envdump" in COMMAND_LINE_TARGETS:
    click.echo(env.Dump())
    env.Exit(0)

if env.IsIntegrationDump():
    projenv = None
    try:
        Import("projenv")
    except:  # pylint: disable=bare-except
        projenv = env
    data = projenv.DumpIntegrationData(env)
    # dump to file for the further reading by project.helpers.load_build_metadata
    with open(
        projenv.subst(os.path.join("$BUILD_DIR", "idedata.json")),
        mode="w",
        encoding="utf8",
    ) as fp:
        json.dump(data, fp)
    click.echo("\n%s\n" % json.dumps(data))  # pylint: disable=undefined-variable
    env.Exit(0)

if "sizedata" in COMMAND_LINE_TARGETS:
    AlwaysBuild(
        env.Alias(
            "sizedata",
            DEFAULT_TARGETS,
            env.VerboseAction(env.DumpSizeData, "Generating memory usage report..."),
        )
    )

    Default("sizedata")
