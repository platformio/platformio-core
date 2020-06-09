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

from platformio import fs


def VerboseAction(_, act, actstr):
    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        return act
    return Action(act, actstr)


def PioClean(env, clean_dir):
    if not os.path.isdir(clean_dir):
        print("Build environment is clean")
        env.Exit(0)
    clean_rel_path = os.path.relpath(clean_dir)
    for root, _, files in os.walk(clean_dir):
        for f in files:
            dst = os.path.join(root, f)
            os.remove(dst)
            print(
                "Removed %s"
                % (dst if clean_rel_path.startswith(".") else os.path.relpath(dst))
            )
    print("Done cleaning")
    fs.rmtree(clean_dir)
    env.Exit(0)


def _add_pio_target(  # pylint: disable=too-many-arguments
    env,
    scope,
    name,
    dependencies,
    actions,
    title=None,
    description=None,
    always_build=True,
):
    if "__PIO_TARGETS" not in env:
        env["__PIO_TARGETS"] = {}
    assert name not in env["__PIO_TARGETS"]
    env["__PIO_TARGETS"][name] = dict(
        name=name, scope=scope, title=title, description=description
    )
    target = env.Alias(name, dependencies, actions)
    if always_build:
        AlwaysBuild(target)
    return target


def AddSystemTarget(env, *args, **kwargs):
    return _add_pio_target(env, "system", *args, **kwargs)


def AddCustomTarget(env, *args, **kwargs):
    return _add_pio_target(env, "custom", *args, **kwargs)


def DumpTargets(env):
    print("DumpTargets", id(env))
    targets = env.get("__PIO_TARGETS") or {}
    # pre-fill default system targets
    if (
        not any(t["scope"] == "system" for t in targets.values())
        and env.PioPlatform().is_embedded()
    ):
        targets["upload"] = dict(name="upload", scope="system", title="Upload")
    targets["compiledb"] = dict(
        name="compiledb",
        scope="system",
        title="Compilation database",
        description="Generate compilation database `compile_commands.json`",
    )
    targets["clean"] = dict(name="clean", scope="system", title="Clean")
    return list(targets.values())


def exists(_):
    return True


def generate(env):
    env.AddMethod(VerboseAction)
    env.AddMethod(PioClean)
    env.AddMethod(AddSystemTarget)
    env.AddMethod(AddCustomTarget)
    env.AddMethod(DumpTargets)
    return env
