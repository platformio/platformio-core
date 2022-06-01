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

from platformio.account.team.commands.add import team_add_cmd
from platformio.account.team.commands.create import team_create_cmd
from platformio.account.team.commands.destroy import team_destroy_cmd
from platformio.account.team.commands.list import team_list_cmd
from platformio.account.team.commands.remove import team_remove_cmd
from platformio.account.team.commands.update import team_update_cmd


@click.group(
    "team",
    commands=[
        team_add_cmd,
        team_create_cmd,
        team_destroy_cmd,
        team_list_cmd,
        team_remove_cmd,
        team_update_cmd,
    ],
    short_help="Manage organization teams",
)
def cli():
    pass
