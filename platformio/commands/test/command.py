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
from platformio.commands.run.helpers import print_header
from platformio.commands.test.embedded import EmbeddedTestProcessor
from platformio.commands.test.native import NativeTestProcessor
from platformio.project.config import ProjectConfig
from platformio.project.helpers import get_project_test_dir


@click.command("test", short_help="Unit Testing")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option("--filter",
              "-f",
              multiple=True,
              metavar="<pattern>",
              help="Filter tests by a pattern")
@click.option("--ignore",
              "-i",
              multiple=True,
              metavar="<pattern>",
              help="Ignore tests by a pattern")
@click.option("--upload-port")
@click.option("--test-port")
@click.option("-d",
              "--project-dir",
              default=getcwd,
              type=click.Path(exists=True,
                              file_okay=False,
                              dir_okay=True,
                              writable=True,
                              resolve_path=True))
@click.option("-c",
              "--project-conf",
              type=click.Path(exists=True,
                              file_okay=True,
                              dir_okay=False,
                              readable=True,
                              resolve_path=True))
@click.option("--without-building", is_flag=True)
@click.option("--without-uploading", is_flag=True)
@click.option("--without-testing", is_flag=True)
@click.option("--no-reset", is_flag=True)
@click.option("--monitor-rts",
              default=None,
              type=click.IntRange(0, 1),
              help="Set initial RTS line state for Serial Monitor")
@click.option("--monitor-dtr",
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
        test_dir = get_project_test_dir()
        if not isdir(test_dir):
            raise exception.TestDirNotExists(test_dir)
        test_names = get_test_names(test_dir)

        config = ProjectConfig.get_instance(
            project_conf or join(project_dir, "platformio.ini"))
        config.validate(envs=environment)

        click.echo("Verbose mode can be enabled via `-v, --verbose` option")
        click.echo("Collected %d items" % len(test_names))

        results = []
        start_time = time()
        default_envs = config.default_envs()
        for testname in test_names:
            for envname in config.envs():
                section = "env:%s" % envname

                # filter and ignore patterns
                patterns = dict(filter=list(filter), ignore=list(ignore))
                for key in patterns:
                    patterns[key].extend(
                        config.get(section, "test_%s" % key, []))

                skip_conditions = [
                    environment and envname not in environment,
                    not environment and default_envs
                    and envname not in default_envs,
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

                cls = (NativeTestProcessor
                       if config.get(section, "platform") == "native" else
                       EmbeddedTestProcessor)
                tp = cls(
                    ctx, testname, envname,
                    dict(project_config=config,
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

    passed_nums = 0
    failed_nums = 0
    testname_max_len = max([len(r[1]) for r in results])
    envname_max_len = max([len(click.style(r[2], fg="cyan")) for r in results])

    print_header("[%s]" % click.style("TEST SUMMARY"))
    click.echo()

    for result in results:
        status, testname, envname = result
        if status is False:
            failed_nums += 1
            status_str = click.style("FAILED", fg="red")
        elif status is None:
            status_str = click.style("IGNORED", fg="yellow")
        else:
            passed_nums += 1
            status_str = click.style("PASSED", fg="green")

        format_str = "test/{:<%d} > {:<%d}\t[{}]" % (testname_max_len,
                                                     envname_max_len)
        click.echo(format_str.format(testname, click.style(envname, fg="cyan"),
                                     status_str),
                   err=status is False)

    print_header("%s%d passed in %.2f seconds" %
                 ("%d failed, " % failed_nums if failed_nums else "",
                  passed_nums, time() - start_time),
                 is_error=failed_nums,
                 fg="red" if failed_nums else "green")

    if failed_nums:
        raise exception.ReturnErrorCode(1)


def get_test_names(test_dir):
    names = []
    for item in sorted(listdir(test_dir)):
        if isdir(join(test_dir, item)):
            names.append(item)
    if not names:
        names = ["*"]
    return names
