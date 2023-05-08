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

import os
import random
from glob import glob

import pytest

from platformio import fs, proc
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectError


def pytest_generate_tests(metafunc):
    if "pioproject_dir" not in metafunc.fixturenames:
        return
    examples_dirs = []

    # repo examples
    examples_dirs.append(
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    )

    # dev/platforms
    for pkg in PlatformPackageManager().get_installed():
        p = PlatformFactory.new(pkg)
        examples_dir = os.path.join(p.get_dir(), "examples")
        if os.path.isdir(examples_dir):
            examples_dirs.append(examples_dir)

    project_dirs = []
    for examples_dir in examples_dirs:
        candidates = {}
        for root, _, files in os.walk(examples_dir):
            if "platformio.ini" not in files or ".skiptest" in files:
                continue
            if "mbed-legacy-examples" in root:
                continue
            group = os.path.basename(root)
            if "-" in group:
                group = group.split("-", 1)[0]
            if group not in candidates:
                candidates[group] = []
            candidates[group].append(root)

        project_dirs.extend(
            [random.choice(examples) for examples in candidates.values() if examples]
        )

    metafunc.parametrize("pioproject_dir", sorted(project_dirs))


def test_run(pioproject_dir):
    with fs.cd(pioproject_dir):
        config = ProjectConfig()

        # temporary fix for unreleased dev-platforms with broken env name
        try:
            config.validate()
        except ProjectError as exc:
            pytest.skip(str(exc))

        build_dir = config.get("platformio", "build_dir")
        if os.path.isdir(build_dir):
            fs.rmtree(build_dir)

        env_names = config.envs()
        result = proc.exec_command(
            ["platformio", "run", "-e", random.choice(env_names)]
        )
        if result["returncode"] != 0:
            pytest.fail(str(result))

        assert os.path.isdir(build_dir)

        # check .elf file
        for item in os.listdir(build_dir):
            if not os.path.isdir(item):
                continue
            assert os.path.isfile(os.path.join(build_dir, item, "firmware.elf"))
            # check .hex or .bin files
            firmwares = []
            for ext in ("bin", "hex"):
                firmwares += glob(os.path.join(build_dir, item, "firmware*.%s" % ext))
            if not firmwares:
                pytest.fail("Missed firmware file")
            for firmware in firmwares:
                assert os.path.getsize(firmware) > 0
