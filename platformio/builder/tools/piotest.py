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

from __future__ import absolute_import

from os.path import join, sep

from platformio.managers.core import get_core_package_dir


def ProcessTest(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST", "UNITY_INCLUDE_CONFIG_H"],
        CPPPATH=[join("$BUILD_DIR", "UnityTestLib")])
    unitylib = env.BuildLibrary(
        join("$BUILD_DIR", "UnityTestLib"), get_core_package_dir("tool-unity"))
    env.Prepend(LIBS=[unitylib])

    src_filter = None
    if "PIOTEST" in env:
        src_filter = "+<output_export.cpp>"
        src_filter += " +<%s%s>" % (env['PIOTEST'], sep)

    return env.CollectBuildFiles(
        "$BUILDTEST_DIR",
        "$PROJECTTEST_DIR",
        src_filter=src_filter,
        duplicate=False)


def exists(_):
    return True


def generate(env):
    env.AddMethod(ProcessTest)
    return env
