# Copyright 2014-present PlatformIO <contact@platformio.org>
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

# pylint: disable=R0913,R0914

from fnmatch import fnmatch
from os import getcwd, listdir
from os.path import isdir, join
from time import sleep, time

import click
import serial

from platformio import exception, util
from platformio.commands.run import cli as cmd_run
from platformio.commands.run import check_project_envs, print_header
from platformio.managers.platform import PlatformFactory


@click.command("test", short_help="Unit Testing")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option("--skip", multiple=True, metavar="<pattern>")
@click.option("--upload-port", metavar="<upload port>")
@click.option("-d", "--project-dir", default=getcwd,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, environment, skip, upload_port, project_dir, verbose):
    assert check_project_envs(project_dir, environment)
    with util.cd(project_dir):
        test_dir = util.get_projecttest_dir()
        if not isdir(test_dir):
            raise exception.TestDirEmpty(test_dir)
        test_names = get_test_names(test_dir)
        projectconf = util.load_project_config()

    click.echo("Collected %d items" % len(test_names))
    click.echo()

    start_time = time()
    results = []
    for testname in test_names:
        for envname in projectconf.sections():
            if not envname.startswith("env:"):
                continue
            envname = envname[4:]
            if environment and envname not in environment:
                continue

            # check skip patterns
            if testname != "*" and any([fnmatch(testname, p) for p in skip]):
                results.append((None, testname, envname))
                continue

            tp = TestProcessor(ctx, testname, envname, {
                "project_config": projectconf,
                "project_dir": project_dir,
                "upload_port": upload_port,
                "verbose": verbose
            })
            results.append((tp.process(), testname, envname))

    click.echo()
    print_header("[%s]" % click.style("TEST SUMMARY"))

    passed = True
    for result in results:
        status, testname, envname = result
        status_str = click.style("PASSED", fg="green")
        if status is False:
            passed = False
            status_str = click.style("FAILED", fg="red")
        elif status is None:
            status_str = click.style("IGNORED", fg="yellow")

        click.echo("test:%s/env:%s\t%s" % (
            click.style(testname, fg="yellow"),
            click.style(envname, fg="cyan"),
            status_str), err=status is False)

    print_header("[%s] Took %.2f seconds" % (
        (click.style("PASSED", fg="green", bold=True) if passed
         else click.style("FAILED", fg="red", bold=True)),
        time() - start_time
    ), is_error=not passed)

    if not passed:
        raise exception.ReturnErrorCode()


class TestProcessor(object):

    SERIAL_TIMEOUT = 600
    SERIAL_BAUDRATE = 9600

    def __init__(self, cmd_ctx, testname, envname, options):
        self.cmd_ctx = cmd_ctx
        self.cmd_ctx.meta['piotest_processor'] = True
        self.test_name = testname
        self.env_name = envname
        self.options = options

    def process(self):
        self._progress("Building... (1/3)")
        self._build_or_upload(["test"])
        self._progress("Uploading... (2/3)")
        self._build_or_upload(["test", "upload"])
        self._progress("Testing... (3/3)")
        sleep(1.0)  # wait while board is starting...
        return self._run_hardware_test()

    def _progress(self, text, is_error=False):
        print_header("[test::%s] %s" % (
            click.style(self.test_name, fg="yellow", bold=True),
            text
        ), is_error=is_error)
        click.echo()

    def _build_or_upload(self, target):
        if self.test_name != "*":
            self.cmd_ctx.meta['piotest'] = self.test_name
        return self.cmd_ctx.invoke(
            cmd_run, project_dir=self.options['project_dir'],
            upload_port=self.options['upload_port'],
            verbose=self.options['verbose'],
            environment=[self.env_name],
            target=target
        )

    def _run_hardware_test(self):
        click.echo("If you don't see any output for the first 10 secs, "
                   "please reset board (press reset button)")
        click.echo()
        ser = serial.Serial(self.get_serial_port(), self.SERIAL_BAUDRATE,
                            timeout=self.SERIAL_TIMEOUT)
        passed = True
        while True:
            line = ser.readline().strip()
            if not line:
                continue
            if line.endswith(":PASS"):
                click.echo("%s\t%s" % (
                    line[:-5], click.style("PASSED", fg="green")))
            elif ":FAIL:" in line:
                passed = False
                click.echo("%s\t%s" % (
                    line, click.style("FAILED", fg="red")))
            else:
                click.echo(line)
            if all([l in line for l in ("Tests", "Failures", "Ignored")]):
                break
        ser.close()
        return passed

    def get_serial_port(self):
        config = self.options['project_config']
        envdata = {}
        for k, v in config.items("env:" + self.env_name):
            envdata[k] = v

        # if upload port is specified manually
        if self.options.get("upload_port", envdata.get("upload_port")):
            return self.options.get("upload_port", envdata.get("upload_port"))

        p = PlatformFactory.newPlatform(envdata['platform'])
        bconfig = p.board_config(envdata['board'])

        port = None
        board_hwids = []
        if "build.hwids" in bconfig:
            board_hwids = bconfig.get("build.hwids")
        for item in util.get_serialports():
            if "VID:PID" not in item['hwid']:
                continue
            port = item['port']
            for hwid in board_hwids:
                hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if hwid_str in item['hwid']:
                    return port
        if not port:
            raise exception.PlatformioException(
                "Please specify `upload_port` for environment or use "
                "global `--upload-port` option.")
        return port


def get_test_names(test_dir):
    names = []
    for item in sorted(listdir(test_dir)):
        if isdir(join(test_dir, item)):
            names.append(item)
    if not names:
        names = ["*"]
    return names
