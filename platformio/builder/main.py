# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import isdir, join

from SCons.Script import (DefaultEnvironment, Exit, SConscript,
                          SConscriptChdir, Variables)

from platformio.util import get_home_dir, get_project_dir, get_source_dir


PIOBUILDER_DIR = join(get_source_dir(), "builder")
# AllowSubstExceptions()

# define user's variables
clivars = Variables(None)
clivars.AddVariables(
    ("PIOENV",),
    ("PLATFORM",),
    ("BOARD",),
    ("UPLOAD_PORT",)
)

# print sdf

DefaultEnvironment(
    tools=["default", "platformio"],
    toolpath=[join(PIOBUILDER_DIR, "tools")],
    variables=clivars,

    PROJECT_DIR=get_project_dir(),

    PLATFORMIOHOME_DIR=get_home_dir(),
    PLATFORM_DIR=join("$PLATFORMIOHOME_DIR", "${PLATFORM}"),
    PLATFORMCORE_DIR=join("$PLATFORM_DIR", "core"),
    PLATFORMTOOLS_DIR=join("$PLATFORM_DIR", "tools"),

    BUILD_DIR=join("$PROJECT_DIR", ".pioenvs", "${PIOENV}"),
    BUILDCORE_DIR=join("$BUILD_DIR", "core"),
    BUILDSRC_DIR=join("$BUILD_DIR", "src")
)

PLATFORM = DefaultEnvironment().subst("${PLATFORM}")

if not isdir(DefaultEnvironment().subst("$PLATFORMIOHOME_DIR")):
    Exit("You haven't installed any platforms yet. Please use"
         "`platformio install` command")
elif not isdir(DefaultEnvironment().subst("$PLATFORM_DIR")):
    Exit("An '%s' platform hasn't been installed yet. Please use "
         "`platformio install %s` command" % (PLATFORM.upper(),
                                              PLATFORM))

SConscriptChdir(0)
SConscript(join(PIOBUILDER_DIR, "scripts", PLATFORM + ".py"))
