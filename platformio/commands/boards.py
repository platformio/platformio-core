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

import json

import click

from platformio.exception import APIRequestError, InternetIsOffline
from platformio.managers.platform import PlatformManager


@click.command("boards", short_help="Embedded Board Explorer")
@click.argument("query", required=False)
@click.option("--installed", is_flag=True)
@click.option("--json-output", is_flag=True)
def cli(query, installed, json_output):  # pylint: disable=R0912
    if json_output:
        return _print_boards_json(query, installed)

    grpboards = {}
    for board in _get_boards(installed):
        if query and query.lower() not in json.dumps(board).lower():
            continue
        if board['platform'] not in grpboards:
            grpboards[board['platform']] = []
        grpboards[board['platform']].append(board)

    terminal_width, _ = click.get_terminal_size()
    for (platform, boards) in sorted(grpboards.items()):
        click.echo("")
        click.echo("Platform: ", nl=False)
        click.secho(platform, bold=True)
        click.echo("-" * terminal_width)
        print_boards(boards)


def print_boards(boards):
    terminal_width, _ = click.get_terminal_size()
    BOARDLIST_TPL = ("{type:<30} {mcu:<14} {frequency:<8} "
                     " {flash:<7} {ram:<6} {name}")
    click.echo(
        BOARDLIST_TPL.format(
            type=click.style("ID", fg="cyan"),
            mcu="MCU",
            frequency="Frequency",
            flash="Flash",
            ram="RAM",
            name="Name"))
    click.echo("-" * terminal_width)

    for board in boards:
        ram_size = board['ram']
        if ram_size >= 1024:
            if ram_size % 1024:
                ram_size = "%.1fkB" % (ram_size / 1024.0)
            else:
                ram_size = "%dkB" % (ram_size / 1024)
        else:
            ram_size = "%dB" % ram_size

        click.echo(
            BOARDLIST_TPL.format(
                type=click.style(board['id'], fg="cyan"),
                mcu=board['mcu'],
                frequency="%dMhz" % (board['fcpu'] / 1000000),
                flash="%dkB" % (board['rom'] / 1024),
                ram=ram_size,
                name=board['name']))


def _get_boards(installed=False):
    boards = PlatformManager().get_installed_boards()
    if not installed:
        know_boards = ["%s:%s" % (b['platform'], b['id']) for b in boards]
        try:
            for board in PlatformManager().get_registered_boards():
                key = "%s:%s" % (board['platform'], board['id'])
                if key not in know_boards:
                    boards.append(board)
        except InternetIsOffline:
            pass
    return sorted(boards, key=lambda b: b['name'])


def _print_boards_json(query, installed=False):
    result = []
    try:
        boards = _get_boards(installed)
    except APIRequestError:
        if not installed:
            boards = _get_boards(True)
    for board in boards:
        if query:
            search_data = "%s %s" % (board['id'], json.dumps(board).lower())
            if query.lower() not in search_data.lower():
                continue
        result.append(board)
    click.echo(json.dumps(result))
