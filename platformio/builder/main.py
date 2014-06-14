# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import isdir, join

from SCons.Script import (DefaultEnvironment, Exit, SConscript,
                          SConscriptChdir, Variables)

from platformio.util import get_home_dir, get_project_dir, get_source_dir

# AllowSubstExceptions()

# allow common variables from INI file
commonvars = Variables(None)
commonvars.AddVariables(
    ("PIOENV",),
    ("PLATFORM",),
    ("FRAMEWORK",),

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
    tools=["default", "platformio"],
    toolpath=[join("$PIOBUILDER_DIR", "tools")],
    variables=commonvars,

    PIOBUILDER_DIR=join(get_source_dir(), "builder"),
    PROJECT_DIR=get_project_dir(),

    PLATFORMIOHOME_DIR=get_home_dir(),
    PLATFORM_DIR=join("$PLATFORMIOHOME_DIR", "$PLATFORM"),
    PLATFORMFW_DIR=join("$PLATFORM_DIR", "frameworks", "$FRAMEWORK"),
    PLATFORMTOOLS_DIR=join("$PLATFORM_DIR", "tools"),

    BUILD_DIR=join("$PROJECT_DIR", ".pioenvs", "$PIOENV"),
    LIBSOURCE_DIRS=[
        join("$PROJECT_DIR", "lib"),
        join("$PLATFORMFW_DIR", "libraries"),
    ]
)

env = DefaultEnvironment()

if not isdir(env['PLATFORMIOHOME_DIR']):
    Exit("You haven't installed any platforms yet. Please use "
         "`platformio install` command")
elif not isdir(env.subst("$PLATFORM_DIR")):
    Exit("An '%s' platform hasn't been installed yet. Please use "
         "`platformio install %s` command" % (env['PLATFORM'],
                                              env['PLATFORM']))

SConscriptChdir(0)
SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "${PLATFORM}.py")))
