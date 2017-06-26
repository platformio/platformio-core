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
from os import getcwd

import click

from platformio.managers.core import pioplus_call


@click.command(
    "debug",
    context_settings=dict(ignore_unknown_options=True),
    short_help="PIO Unified Debugger")
@click.option(
    "-d",
    "--project-dir",
    default=getcwd,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True))
@click.option("--environment", "-e", metavar="<environment>")
@click.option("--verbose", "-v", is_flag=True)
@click.option("--interface", type=click.Choice(["gdb"]))
@click.argument("__unprocessed", nargs=-1, type=click.UNPROCESSED)
def cli(*args, **kwargs):  # pylint: disable=unused-argument
    pioplus_call(sys.argv[1:])
