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

from platformio.system.commands.completion import system_completion_cmd
from platformio.system.commands.info import system_info_cmd
from platformio.system.commands.prune import system_prune_cmd


@click.group(
    "system",
    commands=[
        system_completion_cmd,
        system_info_cmd,
        system_prune_cmd,
    ],
    short_help="Miscellaneous system commands",
)
def cli():
    pass
