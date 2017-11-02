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

import sys

import click

from platformio.managers.core import pioplus_call


@click.command("home", short_help="PIO Home")
@click.option("--port", type=int, default=8008, help="HTTP port, default=8008")
@click.option(
    "--host",
    default="127.0.0.1",
    help="HTTP host, default=127.0.0.1. "
    "You can open PIO Home for inbound connections with --host=0.0.0.0")
@click.option("--no-open", is_flag=True)
def cli(*args, **kwargs):  # pylint: disable=unused-argument
    pioplus_call(sys.argv[1:])
