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
@click.option("--ignore", "-i", multiple=True, metavar="<pattern>")
@click.option("--upload-port", metavar="<upload port>")
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
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, environment, ignore, upload_port, project_dir, verbose):
    with util.cd(project_dir):
        test_dir = util.get_projecttest_dir()
        if not isdir(test_dir):
            raise exception.TestDirEmpty(test_dir)
        test_names = get_test_names(test_dir)
        projectconf = util.load_project_config()
        assert check_project_envs(projectconf, environment)

    click.echo("Verbose mode can be enabled via `-v, --verbose` option")
    click.echo("Collected %d items" % len(test_names))

    start_time = time()
    results = []
    for testname in test_names:
        for section in projectconf.sections():
            if not section.startswith("env:"):
                continue

            envname = section[4:]
            if environment and envname not in environment:
                continue

            # check ignore patterns
            _ignore = list(ignore)
            if projectconf.has_option(section, "test_ignore"):
                _ignore.extend([
                    p.strip()
                    for p in projectconf.get(section, "test_ignore").split(",")
                    if p.strip()
                ])
            if testname != "*" and \
               any([fnmatch(testname, p) for p in _ignore]):
                results.append((None, testname, envname))
                continue

            cls = (LocalTestProcessor
                   if projectconf.get(section, "platform") == "native" else
                   EmbeddedTestProcessor)
            tp = cls(ctx, testname, envname, {
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

        click.echo(
            "test:%s/env:%s\t[%s]" % (click.style(
                testname, fg="yellow"), click.style(
                    envname, fg="cyan"), status_str),
            err=status is False)

    print_header(
        "[%s] Took %.2f seconds" % ((click.style(
            "PASSED", fg="green", bold=True) if passed else click.style(
                "FAILED", fg="red", bold=True)), time() - start_time),
        is_error=not passed)

    if not passed:
        raise exception.ReturnErrorCode()


class TestProcessorBase(object):

    def __init__(self, cmd_ctx, testname, envname, options):
        self.cmd_ctx = cmd_ctx
        self.cmd_ctx.meta['piotest_processor'] = True
        self.test_name = testname
        self.env_name = envname
        self.options = options
        self._run_failed = False

    def print_progress(self, text, is_error=False):
        click.echo()
        print_header(
            "[test::%s] %s" % (click.style(
                self.test_name, fg="yellow", bold=True), text),
            is_error=is_error)

    def build_or_upload(self, target):
        if self.test_name != "*":
            self.cmd_ctx.meta['piotest'] = self.test_name
        return self.cmd_ctx.invoke(
            cmd_run,
            project_dir=self.options['project_dir'],
            upload_port=self.options['upload_port'],
            silent=not self.options['verbose'],
            environment=[self.env_name],
            target=target)

    def run(self):
        raise NotImplementedError

    def on_run_out(self, line):
        if line.endswith(":PASS"):
            click.echo("%s\t[%s]" % (line[:-5], click.style(
                "PASSED", fg="green")))
        elif ":FAIL:" in line:
            self._run_failed = True
            click.echo("%s\t[%s]" % (line, click.style("FAILED", fg="red")))
        else:
            click.echo(line)


class LocalTestProcessor(TestProcessorBase):

    def process(self):
        self.print_progress("Building... (1/2)")
        self.build_or_upload(["test"])
        self.print_progress("Testing... (2/2)")
        return self.run()

    def run(self):
        with util.cd(self.options['project_dir']):
            pioenvs_dir = util.get_projectpioenvs_dir()
        result = util.exec_command(
            [join(pioenvs_dir, self.env_name, "program")],
            stdout=util.AsyncPipe(self.on_run_out),
            stderr=util.AsyncPipe(self.on_run_out))
        assert "returncode" in result
        return result['returncode'] == 0 and not self._run_failed


class EmbeddedTestProcessor(TestProcessorBase):

    SERIAL_TIMEOUT = 600
    SERIAL_BAUDRATE = 9600

    def process(self):
        self.print_progress("Building... (1/3)")
        self.build_or_upload(["test"])
        self.print_progress("Uploading... (2/3)")
        self.build_or_upload(["test", "upload"])
        self.print_progress("Testing... (3/3)")
        sleep(1.0)  # wait while board is starting...
        return self.run()

    def run(self):
        click.echo("If you don't see any output for the first 10 secs, "
                   "please reset board (press reset button)")
        click.echo()
        ser = serial.Serial(
            self.get_serial_port(),
            self.SERIAL_BAUDRATE,
            timeout=self.SERIAL_TIMEOUT)
        while True:
            line = ser.readline().strip()

            # fix non-ascii output from device
            for i, c in enumerate(line[::-1]):
                if ord(c) > 127:
                    line = line[-i:]
                    break

            if not line:
                continue
            self.on_run_out(line)
            if all([l in line for l in ("Tests", "Failures", "Ignored")]):
                break
        ser.close()
        return not self._run_failed

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
