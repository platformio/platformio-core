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

import os
import sys
import threading
from tempfile import mkdtemp
from time import sleep

import click

from platformio import exception, fs
from platformio.commands.device import helpers as device_helpers
from platformio.commands.device.command import device_monitor as cmd_device_monitor
from platformio.managers.core import pioplus_call
from platformio.project.exception import NotPlatformIOProjectError

# pylint: disable=unused-argument


@click.group("remote", short_help="PIO Remote")
@click.option("-a", "--agent", multiple=True)
def cli(**kwargs):
    pass


@cli.group("agent", short_help="Start new agent or list active")
def remote_agent():
    pass


@remote_agent.command("start", short_help="Start agent")
@click.option("-n", "--name")
@click.option("-s", "--share", multiple=True, metavar="E-MAIL")
@click.option(
    "-d",
    "--working-dir",
    envvar="PLATFORMIO_REMOTE_AGENT_DIR",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def remote_agent_start(**kwargs):
    pioplus_call(sys.argv[1:])


@remote_agent.command("reload", short_help="Reload agents")
def remote_agent_reload():
    pioplus_call(sys.argv[1:])


@remote_agent.command("list", short_help="List active agents")
def remote_agent_list():
    pioplus_call(sys.argv[1:])


@cli.command("update", short_help="Update installed Platforms, Packages and Libraries")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="DEPRECATED. Please use `--dry-run` instead",
)
@click.option(
    "--dry-run", is_flag=True, help="Do not update, only check for the new versions"
)
def remote_update(only_check, dry_run):
    pioplus_call(sys.argv[1:])


@cli.command("run", short_help="Process project environments remotely")
@click.option("-e", "--environment", multiple=True)
@click.option("-t", "--target", multiple=True)
@click.option("--upload-port")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option("--disable-auto-clean", is_flag=True)
@click.option("-r", "--force-remote", is_flag=True)
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
def remote_run(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("test", short_help="Remote Unit Testing")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option("--ignore", "-i", multiple=True, metavar="<pattern>")
@click.option("--upload-port")
@click.option("--test-port")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option("-r", "--force-remote", is_flag=True)
@click.option("--without-building", is_flag=True)
@click.option("--without-uploading", is_flag=True)
@click.option("--verbose", "-v", is_flag=True)
def remote_test(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.group("device", short_help="Monitor remote device or list existing")
def remote_device():
    pass


@remote_device.command("list", short_help="List remote devices")
@click.option("--json-output", is_flag=True)
def device_list(json_output):
    pioplus_call(sys.argv[1:])


@remote_device.command("monitor", short_help="Monitor remote device")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option("--baud", "-b", type=int, help="Set baud rate, default=9600")
@click.option(
    "--parity",
    default="N",
    type=click.Choice(["N", "E", "O", "S", "M"]),
    help="Set parity, default=N",
)
@click.option("--rtscts", is_flag=True, help="Enable RTS/CTS flow control, default=Off")
@click.option(
    "--xonxoff", is_flag=True, help="Enable software flow control, default=Off"
)
@click.option(
    "--rts", default=None, type=click.IntRange(0, 1), help="Set initial RTS line state"
)
@click.option(
    "--dtr", default=None, type=click.IntRange(0, 1), help="Set initial DTR line state"
)
@click.option("--echo", is_flag=True, help="Enable local echo, default=Off")
@click.option(
    "--encoding",
    default="UTF-8",
    help="Set the encoding for the serial port (e.g. hexlify, "
    "Latin1, UTF-8), default: UTF-8",
)
@click.option("--filter", "-f", multiple=True, help="Add text transformation")
@click.option(
    "--eol",
    default="CRLF",
    type=click.Choice(["CR", "LF", "CRLF"]),
    help="End of line mode, default=CRLF",
)
@click.option("--raw", is_flag=True, help="Do not apply any encodings/transformations")
@click.option(
    "--exit-char",
    type=int,
    default=3,
    help="ASCII code of special character that is used to exit "
    "the application, default=3 (Ctrl+C)",
)
@click.option(
    "--menu-char",
    type=int,
    default=20,
    help="ASCII code of special character that is used to "
    "control miniterm (menu), default=20 (DEC)",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Diagnostics: suppress non-error messages, default=Off",
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "-e",
    "--environment",
    help="Load configuration from `platformio.ini` and specified environment",
)
@click.pass_context
def device_monitor(ctx, **kwargs):
    project_options = {}
    try:
        with fs.cd(kwargs["project_dir"]):
            project_options = device_helpers.get_project_options(kwargs["environment"])
        kwargs = device_helpers.apply_project_monitor_options(kwargs, project_options)
    except NotPlatformIOProjectError:
        pass

    kwargs["baud"] = kwargs["baud"] or 9600

    def _tx_target(sock_dir):
        pioplus_argv = ["remote", "device", "monitor"]
        pioplus_argv.extend(device_helpers.options_to_argv(kwargs, project_options))
        pioplus_argv.extend(["--sock", sock_dir])
        try:
            pioplus_call(pioplus_argv)
        except exception.ReturnErrorCode:
            pass

    sock_dir = mkdtemp(suffix="pioplus")
    sock_file = os.path.join(sock_dir, "sock")
    try:
        t = threading.Thread(target=_tx_target, args=(sock_dir,))
        t.start()
        while t.is_alive() and not os.path.isfile(sock_file):
            sleep(0.1)
        if not t.is_alive():
            return
        with open(sock_file) as fp:
            kwargs["port"] = fp.read()
        ctx.invoke(cmd_device_monitor, **kwargs)
        t.join(2)
    finally:
        fs.rmtree(sock_dir)
