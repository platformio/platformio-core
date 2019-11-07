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

from platformio.project.config import ProjectConfig, ProjectOptions


def GetProjectConfig(env):
    return ProjectConfig.get_instance(env["PROJECT_CONFIG"])


def GetProjectOptions(env, as_dict=False):
    return env.GetProjectConfig().items(env=env["PIOENV"], as_dict=as_dict)


def GetProjectOption(env, option, default=None):
    return env.GetProjectConfig().get("env:" + env["PIOENV"], option, default)


def LoadProjectOptions(env):
    for option, value in env.GetProjectOptions():
        option_meta = ProjectOptions.get("env." + option)
        if (
            not option_meta
            or not option_meta.buildenvvar
            or option_meta.buildenvvar in env
        ):
            continue
        env[option_meta.buildenvvar] = value


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetProjectConfig)
    env.AddMethod(GetProjectOptions)
    env.AddMethod(GetProjectOption)
    env.AddMethod(LoadProjectOptions)
    return env
