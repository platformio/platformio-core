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

import pytest

SCons = pytest.importorskip("SCons")

# pylint: disable=wrong-import-position
from SCons.Script import Environment  # noqa: E402

from platformio.builder.tools import piobuild  # noqa: E402


def _make_env():
    env = Environment(tools=[])
    env.AddMethod(piobuild.ParseFlagsExtended, "ParseFlagsExtended")
    env.AddMethod(piobuild.ProcessFlags, "ProcessFlags")
    return env


@pytest.mark.parametrize(
    "flags, undefined",
    [
        # "-U NAME" with a space used to leak a bare "-U" to the compiler and
        # push NAME into LIBS as a file // Issue #5237
        ("-U LORA_TX_POWER", ["LORA_TX_POWER"]),
        # attached form must keep working (no regression)
        ("-ULORA_TX_POWER", ["LORA_TX_POWER"]),
        ("-U FOO -UBAR", ["FOO", "BAR"]),
    ],
)
def test_process_flags_undefine(flags, undefined):
    env = _make_env()
    env.Append(CPPDEFINES=list(undefined))
    env.ProcessFlags(flags)
    ccflags = env.get("CCFLAGS", [])
    cppdefines = list(env.get("CPPDEFINES", []))
    # no bare "-U" is passed to the compiler
    assert "-U" not in ccflags
    # the macro name is not mistaken for a library file
    assert not env.get("LIBS", [])
    # every requested macro has been undefined
    for name in undefined:
        assert name not in cppdefines


def test_process_flags_undefine_preserves_other_flags():
    env = _make_env()
    env.ProcessFlags("-w -DX=1 -U FOO -Iinc")
    ccflags = env.get("CCFLAGS", [])
    assert "-w" in ccflags
    assert "-U" not in ccflags
    assert ("X", 1) in list(env.get("CPPDEFINES", []))
    assert not env.get("LIBS", [])
