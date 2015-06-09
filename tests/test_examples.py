# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from glob import glob
from os import listdir, walk
from os.path import dirname, getsize, isdir, isfile, join, normpath
from shutil import rmtree

import pytest

from platformio.util import exec_command


def pytest_generate_tests(metafunc):
    if "pioproject_dir" not in metafunc.fixturenames:
        return
    example_dirs = normpath(join(dirname(__file__), "..", "examples"))
    project_dirs = []
    for root, _, files in walk(example_dirs):
        if "platformio.ini" not in files:
            continue
        project_dirs.append(root)
    project_dirs.sort()
    metafunc.parametrize("pioproject_dir", project_dirs)


@pytest.mark.examples
def test_run(platformio_setup, pioproject_dir):
    if isdir(join(pioproject_dir, ".pioenvs")):
        rmtree(join(pioproject_dir, ".pioenvs"))

    result = exec_command(
        ["platformio", "--force", "run", "--project-dir", pioproject_dir]
    )
    if result['returncode'] != 0:
        pytest.fail(result)

    # check .elf file
    pioenvs_dir = join(pioproject_dir, ".pioenvs")
    for item in listdir(pioenvs_dir):
        if not isdir(item):
            continue
        assert isfile(join(pioenvs_dir, item, "firmware.elf"))
        # check .hex or .bin files
        firmwares = []
        for ext in ("bin", "hex"):
            firmwares += glob(join(pioenvs_dir, item, "firmware*.%s" % ext))
        if not firmwares:
            pytest.fail("Missed firmware file")
        for firmware in firmwares:
            assert getsize(firmware) > 0
