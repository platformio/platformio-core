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


@click.command("test", short_help="Local Unit Testing")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option(
    "--filter",
    "-f",
    multiple=True,
    metavar="<pattern>",
    help="Filter tests by a pattern")
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    metavar="<pattern>",
    help="Ignore tests by a pattern")
@click.option("--upload-port")
@click.option("--test-port")
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
@click.option("--without-building", is_flag=True)
@click.option("--without-uploading", is_flag=True)
@click.option(
    "--no-reset",
    is_flag=True,
    help="Disable software reset via Serial.DTR/RST")
@click.option(
    "--monitor-rts",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial RTS line state for Serial Monitor")
@click.option(
    "--monitor-dtr",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial DTR line state for Serial Monitor")
@click.option("--verbose", "-v", is_flag=True)
def cli(*args, **kwargs):  # pylint: disable=unused-argument
    pioplus_call(sys.argv[1:])
