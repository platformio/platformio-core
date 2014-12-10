# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

try:
    from platformio.util import get_home_dir
except ImportError:
    import sys
    for _path in sys.path:
        if "platformio" in _path:
            sys.path.insert(0, _path[:_path.rfind("platformio")-1])
            break
    from platformio.util import get_home_dir

from os.path import join

from SCons.Script import (DefaultEnvironment, SConscript, SConscriptChdir,
                          Variables)

from platformio.util import (get_lib_dir, get_pioenvs_dir, get_project_dir,
                             get_source_dir)

# AllowSubstExceptions()

# allow common variables from INI file
commonvars = Variables(None)
commonvars.AddVariables(
    ("BUILD_SCRIPT",),
    ("PIOENV",),
    ("PLATFORM",),

    # package aliases
    ("PIOPACKAGE_TOOLCHAIN",),
    ("PIOPACKAGE_UPLOADER",),
    ("PIOPACKAGE_FRAMEWORK",),

    # options
    ("FRAMEWORK",),
    ("BUILD_FLAGS",),
    ("SRCBUILD_FLAGS",),

    # board options
    ("BOARD",),
    ("BOARD_MCU",),
    ("BOARD_F_CPU",),

    # upload options
    ("UPLOAD_PORT",),
    ("UPLOAD_PROTOCOL",),
    ("UPLOAD_SPEED",)
)

DefaultEnvironment(
    # TODO Temporary fix for the issue #18
    tools=["default", "gcc", "g++", "ar", "gnulink", "platformio"],
    toolpath=[join("$PIOBUILDER_DIR", "tools")],
    variables=commonvars,

    PIOHOME_DIR=get_home_dir(),
    PROJECT_DIR=get_project_dir(),
    PIOENVS_DIR=get_pioenvs_dir(),

    PIOBUILDER_DIR=join(get_source_dir(), "builder"),
    PIOPACKAGES_DIR=join("$PIOHOME_DIR", "packages"),
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "$PIOPACKAGE_FRAMEWORK"),

    BUILD_DIR=join("$PIOENVS_DIR", "$PIOENV"),
    LIBSOURCE_DIRS=[
        join("$PROJECT_DIR", "lib"),
        get_lib_dir(),
        join("$PLATFORMFW_DIR", "libraries"),
    ]
)

env = DefaultEnvironment()
env.PrependENVPath(
    "PATH",
    env.subst(join("$PIOPACKAGES_DIR", "$PIOPACKAGE_TOOLCHAIN", "bin"))
)

SConscriptChdir(0)
SConscript(env.subst("$BUILD_SCRIPT"))
