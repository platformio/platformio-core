# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio import app


@click.group(short_help="Manage PlatformIO settings")
def cli():
    pass


@cli.command("get", short_help="Get existing setting/-s")
@click.argument("name", required=False)
def settings_get(name):

    list_tpl = "{name:<40} {value:<35} {description}"
    terminal_width, _ = click.get_terminal_size()

    click.echo(list_tpl.format(
        name=click.style("Name", fg="cyan"),
        value=(click.style("Value", fg="green") +
               click.style(" [Default]", fg="yellow")),
        description="Description"
    ))
    click.echo("-" * terminal_width)

    for _name, _data in sorted(app.DEFAULT_SETTINGS.items()):
        if name and name != _name:
            continue
        _value = app.get_setting(_name)

        _value_str = str(_value)
        if isinstance(_value, bool):
            _value_str = "Yes" if _value else "No"
        _value_str = click.style(_value_str, fg="green")

        if _value != _data['value']:
            _defvalue_str = str(_data['value'])
            if isinstance(_data['value'], bool):
                _defvalue_str = "Yes" if _data['value'] else "No"
            _value_str += click.style(" [%s]" % _defvalue_str, fg="yellow")
        else:
            _value_str += click.style(" ", fg="yellow")

        click.echo(list_tpl.format(
            name=click.style(_name, fg="cyan"),
            value=_value_str,
            description=_data['description']
        ))


@cli.command("set", short_help="Set new value for the setting")
@click.argument("name")
@click.argument("value")
@click.pass_context
def settings_set(ctx, name, value):
    app.set_setting(name, value)
    click.secho("The new value for the setting has been set!", fg="green")
    ctx.invoke(settings_get, name=name)


@cli.command("reset", short_help="Reset settings to default")
@click.pass_context
def settings_reset(ctx):
    app.reset_settings()
    click.secho("The settings have been reseted!", fg="green")
    ctx.invoke(settings_get)
