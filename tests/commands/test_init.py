# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import makedirs, getcwd
from os.path import getsize, isdir, isfile, join

from platformio.commands.init import cli
from platformio import exception, util


def validate_pioproject(pioproject_dir):
    pioconf_path = join(pioproject_dir, "platformio.ini")
    assert isfile(pioconf_path) and getsize(pioconf_path) > 0
    assert isdir(join(pioproject_dir, "src")) and isdir(
        join(pioproject_dir, "lib"))


def test_init_default(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli)
        validate_cliresult(result)
        validate_pioproject(getcwd())


def test_init_ext_folder(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        ext_folder_name = "ext_folder"
        makedirs(ext_folder_name)
        result = clirunner.invoke(cli, ["-d", ext_folder_name])
        validate_cliresult(result)
        validate_pioproject(join(getcwd(), ext_folder_name))


def test_init_special_board(platformio_setup, clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli, ["-b", "uno"])
        validate_cliresult(result)
        validate_pioproject(getcwd())

        uno = util.get_boards("uno")
        config = util.get_project_config()
        expected_result = [
            ('platform', uno['platform']),
            ('framework', uno['framework']),
            ('board', 'uno'),
            ('targets', 'upload')
        ]
        assert config.has_section("env:autogen_uno")
        assert config.items("env:autogen_uno") == expected_result


def test_init_disable_auto_uploading(platformio_setup, clirunner,
                                     validate_cliresult):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cli,
                                  ["-b", "uno", "--disable-auto-uploading"])
        validate_cliresult(result)
        validate_pioproject(getcwd())
        config = util.get_project_config()
        expected_result = [
            ('platform', 'atmelavr'),
            ('framework', 'arduino'),
            ('board', 'uno')
        ]
        assert config.has_section("env:autogen_uno")
        assert config.items("env:autogen_uno") == expected_result


def test_init_incorrect_board(clirunner):
    result = clirunner.invoke(cli, ["-b", "missed_board"])
    assert isinstance(result.exception, exception.UnknownBoard)
