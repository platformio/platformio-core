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

from platformio.device.list.command import device_list_cmd
from platformio.device.monitor.command import device_monitor_cmd


@click.group(
    "device",
    commands=[
        device_list_cmd,
        device_monitor_cmd,
    ],
    short_help="Device manager & Serial/Socket monitor",
)
def cli():
    pass
