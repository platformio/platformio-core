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

import click
from tabulate import tabulate

from platformio import app
from platformio.compat import string_types


@click.group(short_help="Manage PlatformIO settings")
def cli():
    pass


@cli.command("get", short_help="Get existing setting/-s")
@click.argument("name", required=False)
def settings_get(name):
    tabular_data = []
    for _name, _data in sorted(app.DEFAULT_SETTINGS.items()):
        if name and name != _name:
            continue
        _value = app.get_setting(_name)

        _value_str = (str(_value)
                      if not isinstance(_value, string_types) else _value)
        if isinstance(_value, bool):
            _value_str = "Yes" if _value else "No"

        if _value != _data['value']:
            _defvalue_str = str(_data['value'])
            if isinstance(_data['value'], bool):
                _defvalue_str = "Yes" if _data['value'] else "No"
            _value_str = click.style(_value_str, fg="yellow")
            _value_str += "%s[%s]" % ("\n" if len(_value_str) > 10 else " ",
                                      _defvalue_str)
        tabular_data.append(
            (click.style(_name, fg="cyan"), _value_str, _data['description']))

    click.echo(
        tabulate(tabular_data,
                 headers=["Name", "Current value [Default]", "Description"]))


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
