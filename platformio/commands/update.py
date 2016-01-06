# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

from platformio.commands.lib import lib_update as cmd_lib_update
from platformio.commands.platforms import \
    platforms_update as cmd_platforms_update


@click.command("update",
               short_help="Update installed Platforms, Packages and Libraries")
@click.pass_context
def cli(ctx):
    ctx.invoke(cmd_platforms_update)
    click.echo()
    ctx.invoke(cmd_lib_update)
