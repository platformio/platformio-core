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

# pylint: disable=too-many-arguments, too-many-locals, too-many-branches

from fnmatch import fnmatch
from os import getcwd, listdir
from os.path import isdir, join
from time import time

import click

from platformio import exception, util
from platformio.commands.run import check_project_envs, print_header
from platformio.commands.test.embedded import EmbeddedTestProcessor
from platformio.commands.test.native import NativeTestProcessor


@click.command("test", short_help="Unit Testing")
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
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True))
@click.option("--without-building", is_flag=True)
@click.option("--without-uploading", is_flag=True)
@click.option("--without-testing", is_flag=True)
@click.option("--no-reset", is_flag=True)
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
@click.pass_context
def cli(  # pylint: disable=redefined-builtin
        ctx, environment, ignore, filter, upload_port, test_port, project_dir,
        project_conf, without_building, without_uploading, without_testing,
        no_reset, monitor_rts, monitor_dtr, verbose):
    with util.cd(project_dir):
        test_dir = util.get_projecttest_dir()
        if not isdir(test_dir):
            raise exception.TestDirNotExists(test_dir)
        test_names = get_test_names(test_dir)
        projectconf = util.load_project_config(project_conf)
        env_default = None
        if projectconf.has_option("platformio", "env_default"):
            env_default = util.parse_conf_multi_values(
                projectconf.get("platformio", "env_default"))
        assert check_project_envs(projectconf, environment or env_default)

        click.echo("Verbose mode can be enabled via `-v, --verbose` option")
        click.echo("Collected %d items" % len(test_names))

        start_time = time()
        results = []
        for testname in test_names:
            for section in projectconf.sections():
                if not section.startswith("env:"):
                    continue

                # filter and ignore patterns
                patterns = dict(filter=list(filter), ignore=list(ignore))
                for key in patterns:
                    if projectconf.has_option(section, "test_%s" % key):
                        patterns[key].extend([
                            p.strip()
                            for p in projectconf.get(section, "test_%s" %
                                                     key).split(", ")
                            if p.strip()
                        ])

                envname = section[4:]
                skip_conditions = [
                    environment and envname not in environment,
                    not environment and env_default
                    and envname not in env_default,
                    testname != "*" and patterns['filter'] and
                    not any([fnmatch(testname, p)
                             for p in patterns['filter']]),
                    testname != "*"
                    and any([fnmatch(testname, p)
                             for p in patterns['ignore']]),
                ]
                if any(skip_conditions):
                    results.append((None, testname, envname))
                    continue

                cls = (NativeTestProcessor if projectconf.get(
                    section, "platform") == "native" else
                       EmbeddedTestProcessor)
                tp = cls(
                    ctx, testname, envname,
                    dict(
                        project_config=projectconf,
                        project_dir=project_dir,
                        upload_port=upload_port,
                        test_port=test_port,
                        without_building=without_building,
                        without_uploading=without_uploading,
                        without_testing=without_testing,
                        no_reset=no_reset,
                        monitor_rts=monitor_rts,
                        monitor_dtr=monitor_dtr,
                        verbose=verbose))
                results.append((tp.process(), testname, envname))

    if without_testing:
        return

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
            "test/%s/env:%s\t[%s]" % (click.style(testname, fg="yellow"),
                                      click.style(envname, fg="cyan"),
                                      status_str),
            err=status is False)

    print_header(
        "[%s] Took %.2f seconds" % (
            (click.style("PASSED", fg="green", bold=True) if passed else
             click.style("FAILED", fg="red", bold=True)), time() - start_time),
        is_error=not passed)

    if not passed:
        raise exception.ReturnErrorCode(1)


def get_test_names(test_dir):
    names = []
    for item in sorted(listdir(test_dir)):
        if isdir(join(test_dir, item)):
            names.append(item)
    if not names:
        names = ["*"]
    return names
