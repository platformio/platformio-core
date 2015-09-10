# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

import click

from platformio.util import get_boards


@click.command("list", short_help="Pre-configured Embedded Boards")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def cli(query, json_output):  # pylint: disable=R0912

    if json_output:
        return ouput_boards_json(query)

    BOARDLIST_TPL = ("{type:<30} {mcu:<14} {frequency:<8} "
                     " {flash:<7} {ram:<6} {name}")
    terminal_width, _ = click.get_terminal_size()

    grpboards = {}
    for type_, data in get_boards().items():
        if data['platform'] not in grpboards:
            grpboards[data['platform']] = {}
        grpboards[data['platform']][type_] = data

    for (platform, boards) in sorted(grpboards.items()):
        if query:
            search_data = json.dumps(boards).lower()
            if query.lower() not in search_data.lower():
                continue

        click.echo("")
        click.echo("Platform: ", nl=False)
        click.secho(platform, bold=True)
        click.echo("-" * terminal_width)
        click.echo(BOARDLIST_TPL.format(
            type=click.style("Type", fg="cyan"), mcu="MCU",
            frequency="Frequency", flash="Flash", ram="RAM", name="Name"))
        click.echo("-" * terminal_width)

        for type_, data in sorted(boards.items(), key=lambda b: b[1]['name']):
            if query:
                search_data = "%s %s" % (type_, json.dumps(data).lower())
                if query.lower() not in search_data.lower():
                    continue

            flash_size = ""
            if "maximum_size" in data.get("upload", None):
                flash_size = int(data['upload']['maximum_size'])
                flash_size = "%dKb" % (flash_size / 1024)

            ram_size = ""
            if "maximum_ram_size" in data.get("upload", None):
                ram_size = int(data['upload']['maximum_ram_size'])
                if ram_size >= 1024:
                    if ram_size % 1024:
                        ram_size = "%.1fKb" % (ram_size / 1024.0)
                    else:
                        ram_size = "%dKb" % (ram_size / 1024)
                else:
                    ram_size = "%dB" % ram_size

            click.echo(BOARDLIST_TPL.format(
                type=click.style(type_, fg="cyan"), mcu=data['build']['mcu'],
                frequency="%dMhz" % (
                    int(data['build']['f_cpu'][:-1]) / 1000000),
                flash=flash_size, ram=ram_size, name=data['name']))


def ouput_boards_json(query):
    result = {}
    for type_, data in get_boards().items():
        if query:
            search_data = "%s %s" % (type_, json.dumps(data).lower())
            if query.lower() not in search_data.lower():
                continue
        result[type_] = data
    click.echo(json.dumps(result))
