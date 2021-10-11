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

from __future__ import absolute_import

import os

from SCons.Action import Action  # pylint: disable=import-error
from SCons.Script import ARGUMENTS  # pylint: disable=import-error
from SCons.Script import AlwaysBuild  # pylint: disable=import-error

from platformio import compat, fs


def VerboseAction(_, act, actstr):
    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        return act
    return Action(act, actstr)


def PioClean(env, clean_all=False):
    def _relpath(path):
        if compat.IS_WINDOWS:
            prefix = os.getcwd()[:2].lower()
            if (
                ":" not in prefix
                or not path.lower().startswith(prefix)
                or os.path.relpath(path).startswith("..")
            ):
                return path
        return os.path.relpath(path)

    def _clean_dir(path):
        clean_rel_path = _relpath(path)
        for root, _, files in os.walk(path):
            for f in files:
                dst = os.path.join(root, f)
                os.remove(dst)
                print(
                    "Removed %s"
                    % (dst if not clean_rel_path.startswith(".") else _relpath(dst))
                )

    build_dir = env.subst("$BUILD_DIR")
    libdeps_dir = env.subst("$PROJECT_LIBDEPS_DIR")
    if os.path.isdir(build_dir):
        _clean_dir(build_dir)
        fs.rmtree(build_dir)
    else:
        print("Build environment is clean")

    if clean_all and os.path.isdir(libdeps_dir):
        _clean_dir(libdeps_dir)
        fs.rmtree(libdeps_dir)

    print("Done cleaning")


def AddTarget(  # pylint: disable=too-many-arguments
    env,
    name,
    dependencies,
    actions,
    title=None,
    description=None,
    group="General",
    always_build=True,
):
    if "__PIO_TARGETS" not in env:
        env["__PIO_TARGETS"] = {}
    assert name not in env["__PIO_TARGETS"]
    env["__PIO_TARGETS"][name] = dict(
        name=name, title=title, description=description, group=group
    )
    target = env.Alias(name, dependencies, actions)
    if always_build:
        AlwaysBuild(target)
    return target


def AddPlatformTarget(env, *args, **kwargs):
    return env.AddTarget(group="Platform", *args, **kwargs)


def AddCustomTarget(env, *args, **kwargs):
    return env.AddTarget(group="Custom", *args, **kwargs)


def DumpTargets(env):
    targets = env.get("__PIO_TARGETS") or {}
    # pre-fill default targets if embedded dev-platform
    if env.PioPlatform().is_embedded() and not any(
        t["group"] == "Platform" for t in targets.values()
    ):
        targets["upload"] = dict(name="upload", group="Platform", title="Upload")
    targets["compiledb"] = dict(
        name="compiledb",
        title="Compilation Database",
        description="Generate compilation database `compile_commands.json`",
        group="Advanced",
    )
    targets["clean"] = dict(name="clean", title="Clean", group="General")
    targets["cleanall"] = dict(
        name="cleanall",
        title="Clean All",
        group="General",
        description="Clean a build environment and installed library dependencies",
    )
    return list(targets.values())


def exists(_):
    return True


def generate(env):
    env.AddMethod(VerboseAction)
    env.AddMethod(PioClean)
    env.AddMethod(AddTarget)
    env.AddMethod(AddPlatformTarget)
    env.AddMethod(AddCustomTarget)
    env.AddMethod(DumpTargets)
    return env
