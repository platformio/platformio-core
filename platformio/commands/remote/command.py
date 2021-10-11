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

# pylint: disable=too-many-arguments, import-outside-toplevel
# pylint: disable=inconsistent-return-statements

import os
import subprocess
import threading
from tempfile import mkdtemp
from time import sleep

import click

from platformio import fs, proc
from platformio.commands.device import helpers as device_helpers
from platformio.commands.device.command import device_monitor as cmd_device_monitor
from platformio.commands.run.command import cli as cmd_run
from platformio.commands.test.command import cli as cmd_test
from platformio.package.manager.core import inject_contrib_pysite
from platformio.project.exception import NotPlatformIOProjectError


@click.group("remote", short_help="Remote development")
@click.option("-a", "--agent", multiple=True)
@click.pass_context
def cli(ctx, agent):
    ctx.obj = agent
    inject_contrib_pysite(verify_openssl=True)


@cli.group("agent", short_help="Start a new agent or list active")
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
def remote_agent_start(name, share, working_dir):
    from platformio.commands.remote.client.agent_service import RemoteAgentService

    RemoteAgentService(name, share, working_dir).connect()


@remote_agent.command("list", short_help="List active agents")
def remote_agent_list():
    from platformio.commands.remote.client.agent_list import AgentListClient

    AgentListClient().connect()


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
@click.pass_obj
def remote_update(agents, only_check, dry_run):
    from platformio.commands.remote.client.update_core import UpdateCoreClient

    UpdateCoreClient("update", agents, dict(only_check=only_check or dry_run)).connect()


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
@click.pass_obj
@click.pass_context
def remote_run(
    ctx,
    agents,
    environment,
    target,
    upload_port,
    project_dir,
    disable_auto_clean,
    force_remote,
    silent,
    verbose,
):

    from platformio.commands.remote.client.run_or_test import RunOrTestClient

    cr = RunOrTestClient(
        "run",
        agents,
        dict(
            environment=environment,
            target=target,
            upload_port=upload_port,
            project_dir=project_dir,
            disable_auto_clean=disable_auto_clean,
            force_remote=force_remote,
            silent=silent,
            verbose=verbose,
        ),
    )
    if force_remote:
        return cr.connect()

    click.secho("Building project locally", bold=True)
    local_targets = []
    if "clean" in target:
        local_targets = ["clean"]
    elif set(["buildfs", "uploadfs", "uploadfsota"]) & set(target):
        local_targets = ["buildfs"]
    else:
        local_targets = ["checkprogsize", "buildprog"]
    ctx.invoke(
        cmd_run,
        environment=environment,
        target=local_targets,
        project_dir=project_dir,
        # disable_auto_clean=True,
        silent=silent,
        verbose=verbose,
    )

    if any(["upload" in t for t in target] + ["program" in target]):
        click.secho("Uploading firmware remotely", bold=True)
        cr.options["target"] += ("nobuild",)
        cr.options["disable_auto_clean"] = True
        cr.connect()

    return True


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
@click.pass_obj
@click.pass_context
def remote_test(
    ctx,
    agents,
    environment,
    ignore,
    upload_port,
    test_port,
    project_dir,
    force_remote,
    without_building,
    without_uploading,
    verbose,
):

    from platformio.commands.remote.client.run_or_test import RunOrTestClient

    cr = RunOrTestClient(
        "test",
        agents,
        dict(
            environment=environment,
            ignore=ignore,
            upload_port=upload_port,
            test_port=test_port,
            project_dir=project_dir,
            force_remote=force_remote,
            without_building=without_building,
            without_uploading=without_uploading,
            verbose=verbose,
        ),
    )
    if force_remote:
        return cr.connect()

    click.secho("Building project locally", bold=True)

    ctx.invoke(
        cmd_test,
        environment=environment,
        ignore=ignore,
        project_dir=project_dir,
        without_uploading=True,
        without_testing=True,
        verbose=verbose,
    )

    click.secho("Testing project remotely", bold=True)
    cr.options["without_building"] = True
    cr.connect()

    return True


@cli.group("device", short_help="Monitor remote device or list existing")
def remote_device():
    pass


@remote_device.command("list", short_help="List remote devices")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def device_list(agents, json_output):
    from platformio.commands.remote.client.device_list import DeviceListClient

    DeviceListClient(agents, json_output).connect()


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
@click.option(
    "--sock",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.pass_obj
@click.pass_context
def device_monitor(ctx, agents, **kwargs):
    from platformio.commands.remote.client.device_monitor import DeviceMonitorClient

    if kwargs["sock"]:
        return DeviceMonitorClient(agents, **kwargs).connect()

    project_options = {}
    try:
        with fs.cd(kwargs["project_dir"]):
            project_options = device_helpers.get_project_options(kwargs["environment"])
        kwargs = device_helpers.apply_project_monitor_options(kwargs, project_options)
    except NotPlatformIOProjectError:
        pass

    kwargs["baud"] = kwargs["baud"] or 9600

    def _tx_target(sock_dir):
        subcmd_argv = ["remote"]
        for agent in agents:
            subcmd_argv.extend(["--agent", agent])
        subcmd_argv.extend(["device", "monitor"])
        subcmd_argv.extend(device_helpers.options_to_argv(kwargs, project_options))
        subcmd_argv.extend(["--sock", sock_dir])
        subprocess.call([proc.where_is_program("platformio")] + subcmd_argv)

    sock_dir = mkdtemp(suffix="pio")
    sock_file = os.path.join(sock_dir, "sock")
    try:
        t = threading.Thread(target=_tx_target, args=(sock_dir,))
        t.start()
        while t.is_alive() and not os.path.isfile(sock_file):
            sleep(0.1)
        if not t.is_alive():
            return
        with open(sock_file, encoding="utf8") as fp:
            kwargs["port"] = fp.read()
        ctx.invoke(cmd_device_monitor, **kwargs)
        t.join(2)
    finally:
        fs.rmtree(sock_dir)

    return True
