# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

from os.path import isfile, join

from click.testing import CliRunner

from platformio.commands.boards import cli as boards_cli
from platformio.commands.search import cli as search_cli
from platformio.commands.install import cli as install_cli
from platformio import util

runner = CliRunner()


def validate_output(result):
    assert result.exit_code == 0
    assert not result.exception
    assert "error" not in result.output.lower()


def test_board_json_output(platformio_setup):
    result = runner.invoke(boards_cli, ["cortex", "--json-output"])
    validate_output(result)
    boards = json.loads(result.output)
    assert isinstance(boards, dict)
    assert "teensy30" in boards


def test_board_raw_output(platformio_setup):
    result = runner.invoke(boards_cli, ["energia"])
    validate_output(result)
    assert "titiva" in result.output


def test_board_options(platformio_setup):
    required_opts = set(
        ["build", "platform", "upload", "name"])

    # fetch avaialble platforms
    result = runner.invoke(search_cli, ["--json-output"])
    validate_output(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert len(search_result)
    platforms = [item['name'] for item in search_result]

    for name, opts in util.get_boards().iteritems():
        assert required_opts.issubset(set(opts))
        assert opts['platform'] in platforms


def test_board_ldscripts(platformio_setup):
    result = runner.invoke(
        install_cli, [
            "stm32",
            "--skip-default-package",
            "--with-package=ldscripts"
        ])
    validate_output(result)
    ldscripts_path = join(util.get_home_dir(), "packages", "ldscripts")
    for _, opts in util.get_boards().iteritems():
        if opts['build'].get("ldscript"):
            assert isfile(join(ldscripts_path, opts['build'].get("ldscript")))
