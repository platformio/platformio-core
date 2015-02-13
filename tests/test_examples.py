# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import listdir, walk
from os.path import dirname, getsize, isdir, isfile, join, normpath
from shutil import rmtree

import pytest

from platformio import app
from platformio.util import exec_command


@pytest.fixture(scope="module")
def platformio_setup(request):
    prev_settings = dict(
        enable_telemetry=None,
        enable_prompts=None
    )
    for key, value in prev_settings.iteritems():
        prev_settings[key] = app.get_setting(key)
        # disable temporary
        if prev_settings[key]:
            app.set_setting(key, False)

    def platformio_teardown():
        # restore settings
        for key, value in prev_settings.iteritems():
            app.set_setting(key, value)

    request.addfinalizer(platformio_teardown)


def pytest_generate_tests(metafunc):
    if "pioproject_dir" not in metafunc.fixturenames:
        return
    example_dirs = normpath(join(dirname(__file__), "..", "examples"))
    project_dirs = []
    for root, _, files in walk(example_dirs):
        if "platformio.ini" not in files:
            continue
        project_dirs.append(root)
    metafunc.parametrize("pioproject_dir", project_dirs)


def test_run(platformio_setup, pioproject_dir):
    if isdir(join(pioproject_dir, ".pioenvs")):
        rmtree(join(pioproject_dir, ".pioenvs"))

    result = exec_command(
        ["platformio", "run"],
        cwd=pioproject_dir
    )
    output = "%s\n%s" % (result['out'], result['err'])
    if "error" in output.lower():
        pytest.fail(output)

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
