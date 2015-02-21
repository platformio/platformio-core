# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
        ["platformio", "run"],
        cwd=pioproject_dir
    )
    if result['returncode'] != 0:
        pytest.fail(result)

    # check .elf file
    pioenvs_dir = join(pioproject_dir, ".pioenvs")
    for item in listdir(pioenvs_dir):
        assert isfile(join(pioenvs_dir, item, "firmware.elf"))
        # check .hex or .bin file
        bin_file = join(pioenvs_dir, item, "firmware.bin")
        hex_file = join(pioenvs_dir, item, "firmware.hex")
        if not isfile(bin_file):
            if not isfile(hex_file):
                pytest.fail("Missed firmware file")
            assert getsize(hex_file) > 0
        else:
            assert getsize(bin_file) > 0
