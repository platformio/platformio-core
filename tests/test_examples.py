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

from glob import glob
from os import listdir, walk
from os.path import dirname, getsize, isdir, isfile, join, normpath

import pytest

from platformio import util


def pytest_generate_tests(metafunc):
    if "pioproject_dir" not in metafunc.fixturenames:
        return
    example_dirs = normpath(join(dirname(__file__), "..", "examples"))
    project_dirs = []
    for root, _, files in walk(example_dirs):
        if "platformio.ini" not in files or ".skiptest" in files:
            continue
        project_dirs.append(root)
    project_dirs.sort()
    metafunc.parametrize("pioproject_dir", project_dirs)


@pytest.mark.examples
def test_run(pioproject_dir):
    with util.cd(pioproject_dir):
        build_dir = util.get_projectbuild_dir()
        if isdir(build_dir):
            util.rmtree_(build_dir)

        result = util.exec_command(["platformio", "--force", "run"])
        if result['returncode'] != 0:
            pytest.fail(result)

        assert isdir(build_dir)

        # check .elf file
        for item in listdir(build_dir):
            if not isdir(item):
                continue
            assert isfile(join(build_dir, item, "firmware.elf"))
            # check .hex or .bin files
            firmwares = []
            for ext in ("bin", "hex"):
                firmwares += glob(join(build_dir, item, "firmware*.%s" % ext))
            if not firmwares:
                pytest.fail("Missed firmware file")
            for firmware in firmwares:
                assert getsize(firmware) > 0
