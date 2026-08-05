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

from platformio.builder.tools.piomisc import ConfigureDebugTarget
from platformio.project.options import ProjectOptions


class SConsEnvironmentStub(dict):
    """Reproduces the SCons Environment API used by ConfigureDebugTarget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_project_options = {}

    def Append(self, **kwargs):
        for key, values in kwargs.items():
            self.setdefault(key, []).extend(values)

    def AppendUnique(self, **kwargs):
        for key, values in kwargs.items():
            container = self.setdefault(key, [])
            for value in values:
                if value not in container:
                    container.append(value)

    def MergeFlags(self, parsed_flags):
        self.Append(**parsed_flags)

    def ParseFlags(self, raw_flags):
        ccflags = []
        for item in raw_flags:
            ccflags.extend(item.split())
        return {"CCFLAGS": ccflags}

    def GetProjectOptions(self, as_dict=False):
        assert as_dict
        return self.custom_project_options

    def GetProjectOption(self, name, default=None):
        if name in self.custom_project_options:
            return self.custom_project_options[name]
        option = ProjectOptions.get("env.%s" % name)
        return option.default if option else default


def test_configure_debug_target_default_flags():
    env = SConsEnvironmentStub(
        ASFLAGS=["-mcpu=cortex-m3", "-mthumb", "-g"],
        CCFLAGS=["-mcpu=cortex-m3", "-mthumb", "-Os", "-g"],
        LINKFLAGS=["-mcpu=cortex-m3", "-Os"],
    )
    ConfigureDebugTarget(env)
    # issue #5005: the `as` assembler supports only the plain `-g` flag
    assert env["ASFLAGS"] == ["-mcpu=cortex-m3", "-mthumb", "-g"]
    assert env["CCFLAGS"] == ["-mcpu=cortex-m3", "-mthumb", "-Og", "-g2", "-ggdb2"]
    assert env["LINKFLAGS"] == ["-mcpu=cortex-m3", "-Og", "-g2", "-ggdb2"]
    assert env["CPPDEFINES"] == ["__PLATFORMIO_BUILD_DEBUG__"]


def test_configure_debug_target_custom_flags():
    env = SConsEnvironmentStub(ASFLAGS=["-mthumb"], CCFLAGS=["-mthumb", "-Os"])
    env.custom_project_options["debug_build_flags"] = ["-O0 -ggdb3"]
    ConfigureDebugTarget(env)
    assert env["ASFLAGS"] == ["-mthumb", "-g"]
    assert env["CCFLAGS"] == ["-mthumb", "-O0", "-ggdb3"]
    assert env["LINKFLAGS"] == ["-O0", "-ggdb3"]


def test_configure_debug_target_without_debugging_flags():
    env = SConsEnvironmentStub(ASFLAGS=["-mthumb"], CCFLAGS=["-mthumb", "-Os"])
    env.custom_project_options["debug_build_flags"] = ["-O0"]
    ConfigureDebugTarget(env)
    assert env["ASFLAGS"] == ["-mthumb"]
    assert env["CCFLAGS"] == ["-mthumb", "-O0"]
