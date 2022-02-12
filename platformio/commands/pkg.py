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

from platformio.package.commands.exec import package_exec_cmd
from platformio.package.commands.outdated import package_outdated_cmd
from platformio.package.commands.pack import package_pack_cmd
from platformio.package.commands.publish import package_publish_cmd
from platformio.package.commands.unpublish import package_unpublish_cmd


@click.group(
    "pkg",
    commands=[
        package_exec_cmd,
        package_outdated_cmd,
        package_pack_cmd,
        package_publish_cmd,
        package_unpublish_cmd,
    ],
    short_help="Package Manager",
)
def cli():
    pass
