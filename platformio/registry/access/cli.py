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

from platformio.registry.access.commands.grant import access_grant_cmd
from platformio.registry.access.commands.list import access_list_cmd
from platformio.registry.access.commands.private import access_private_cmd
from platformio.registry.access.commands.public import access_public_cmd
from platformio.registry.access.commands.revoke import access_revoke_cmd


@click.group(
    "access",
    commands=[
        access_grant_cmd,
        access_list_cmd,
        access_private_cmd,
        access_public_cmd,
        access_revoke_cmd,
    ],
    short_help="Manage resource access",
)
def cli():
    pass
