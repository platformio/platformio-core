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

from platformio.project.commands.config import project_config_cmd
from platformio.project.commands.init import project_init_cmd
from platformio.project.commands.metadata import project_metadata_cmd


@click.group(
    "project",
    commands=[
        project_config_cmd,
        project_init_cmd,
        project_metadata_cmd,
    ],
    short_help="Project Manager",
)
def cli():
    pass
