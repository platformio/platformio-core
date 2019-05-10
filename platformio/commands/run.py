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

from os import getcwd, makedirs
from os.path import getmtime, isdir, isfile, join
from time import time

import click

from platformio import exception, telemetry, util
from platformio.commands.device import device_monitor as cmd_device_monitor
from platformio.commands.lib import lib_install as cmd_lib_install
from platformio.commands.platform import \
    platform_install as cmd_platform_install
from platformio.managers.lib import LibraryManager, is_builtin_lib
from platformio.managers.platform import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.helpers import (
    calculate_project_hash, find_project_dir_above, get_project_dir,
    get_projectbuild_dir, get_projectlibdeps_dir)

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches


@click.command("run", short_help="Process project environments")
@click.option("-e", "--environment", multiple=True)
@click.option("-t", "--target", multiple=True)
@click.option("--upload-port")
@click.option(
    "-d",
    "--project-dir",
    default=getcwd,
    type=click.Path(
        exists=True,
        file_okay=True,
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
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--disable-auto-clean", is_flag=True)
@click.pass_context
def cli(ctx, environment, target, upload_port, project_dir, project_conf,
        silent, verbose, disable_auto_clean):
    # find project directory on upper level
    if isfile(project_dir):
        project_dir = find_project_dir_above(project_dir)

    with util.cd(project_dir):
        # clean obsolete build dir
        if not disable_auto_clean:
            try:
                _clean_build_dir(get_projectbuild_dir())
            except:  # pylint: disable=bare-except
                click.secho(
                    "Can not remove temporary directory `%s`. Please remove "
                    "it manually to avoid build issues" %
                    get_projectbuild_dir(force=True),
                    fg="yellow")

        config = ProjectConfig.get_instance(
            project_conf or join(project_dir, "platformio.ini"))
        config.validate(environment)

        results = []
        start_time = time()
        default_envs = config.default_envs()
        for envname in config.envs():
            skipenv = any([
                environment and envname not in environment, not environment
                and default_envs and envname not in default_envs
            ])
            if skipenv:
                results.append((envname, None))
                continue

            if not silent and results:
                click.echo()

            options = config.items(env=envname, as_dict=True)
            if "piotest" not in options and "piotest" in ctx.meta:
                options['piotest'] = ctx.meta['piotest']

            ep = EnvironmentProcessor(ctx, envname, options, target,
                                      upload_port, silent, verbose)
            result = (envname, ep.process())
            results.append(result)
            if result[1] and "monitor" in ep.get_build_targets() and \
                    "nobuild" not in ep.get_build_targets():
                ctx.invoke(
                    cmd_device_monitor,
                    environment=environment[0] if environment else None)

        found_error = any(status is False for (_, status) in results)

        if (found_error or not silent) and len(results) > 1:
            click.echo()
            print_summary(results, start_time)

        if found_error:
            raise exception.ReturnErrorCode(1)
        return True


class EnvironmentProcessor(object):

    DEFAULT_DUMP_OPTIONS = ("platform", "framework", "board")

    IGNORE_BUILD_OPTIONS = [
        "test_transport", "test_filter", "test_ignore", "test_port",
        "test_speed", "debug_port", "debug_init_cmds", "debug_extra_cmds",
        "debug_server", "debug_init_break", "debug_load_cmd",
        "debug_load_mode", "monitor_port", "monitor_speed", "monitor_rts",
        "monitor_dtr"
    ]

    REMAPED_OPTIONS = {"framework": "pioframework", "platform": "pioplatform"}

    def __init__(
            self,  # pylint: disable=R0913
            cmd_ctx,
            name,
            options,
            targets,
            upload_port,
            silent,
            verbose):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.options = options
        self.targets = targets
        self.upload_port = upload_port
        self.silent = silent
        self.verbose = verbose

    def process(self):
        terminal_width, _ = click.get_terminal_size()
        start_time = time()
        env_dump = []

        for k, v in self.options.items():
            self.options[k] = self.options[k].strip()
            if self.verbose or k in self.DEFAULT_DUMP_OPTIONS:
                env_dump.append(
                    "%s: %s" % (k, ", ".join(util.parse_conf_multi_values(v))))

        if not self.silent:
            click.echo("Processing %s (%s)" % (click.style(
                self.name, fg="cyan", bold=True), "; ".join(env_dump)))
            click.secho("-" * terminal_width, bold=True)

        result = self._run()
        is_error = result['returncode'] != 0

        if self.silent and not is_error:
            return True

        if is_error or "piotest_processor" not in self.cmd_ctx.meta:
            print_header(
                "[%s] Took %.2f seconds" % (
                    (click.style("ERROR", fg="red", bold=True) if is_error else
                     click.style("SUCCESS", fg="green", bold=True)),
                    time() - start_time),
                is_error=is_error)

        return not is_error

    def get_build_variables(self):
        variables = {"pioenv": self.name}
        if self.upload_port:
            variables['upload_port'] = self.upload_port
        for k, v in self.options.items():
            if k in self.REMAPED_OPTIONS:
                k = self.REMAPED_OPTIONS[k]
            if k in self.IGNORE_BUILD_OPTIONS:
                continue
            if k == "targets" or (k == "upload_port" and self.upload_port):
                continue
            variables[k] = v
        return variables

    def get_build_targets(self):
        targets = []
        if self.targets:
            targets = [t for t in self.targets]
        elif "targets" in self.options:
            targets = self.options['targets'].split(", ")
        return targets

    def _run(self):
        if "platform" not in self.options:
            raise exception.UndefinedEnvPlatform(self.name)

        build_vars = self.get_build_variables()
        build_targets = self.get_build_targets()

        telemetry.on_run_environment(self.options, build_targets)

        # skip monitor target, we call it above
        if "monitor" in build_targets:
            build_targets.remove("monitor")
        if "nobuild" not in build_targets:
            # install dependent libraries
            if "lib_install" in self.options:
                _autoinstall_libdeps(self.cmd_ctx, [
                    int(d.strip())
                    for d in self.options['lib_install'].split(",")
                    if d.strip()
                ], self.verbose)
            if "lib_deps" in self.options:
                _autoinstall_libdeps(
                    self.cmd_ctx,
                    util.parse_conf_multi_values(self.options['lib_deps']),
                    self.verbose)

        try:
            p = PlatformFactory.newPlatform(self.options['platform'])
        except exception.UnknownPlatform:
            self.cmd_ctx.invoke(
                cmd_platform_install,
                platforms=[self.options['platform']],
                skip_default_package=True)
            p = PlatformFactory.newPlatform(self.options['platform'])

        return p.run(build_vars, build_targets, self.silent, self.verbose)


def _autoinstall_libdeps(ctx, libraries, verbose=False):
    if not libraries:
        return
    storage_dir = get_projectlibdeps_dir()
    ctx.obj = LibraryManager(storage_dir)
    if verbose:
        click.echo("Library Storage: " + storage_dir)
    for lib in libraries:
        try:
            ctx.invoke(cmd_lib_install, libraries=[lib], silent=not verbose)
        except exception.LibNotFound as e:
            if verbose or not is_builtin_lib(lib):
                click.secho("Warning! %s" % e, fg="yellow")
        except exception.InternetIsOffline as e:
            click.secho(str(e), fg="yellow")


def _clean_build_dir(build_dir):
    structhash_file = join(build_dir, "structure.hash")
    proj_hash = calculate_project_hash()

    # if project's config is modified
    if (isdir(build_dir) and getmtime(
            join(get_project_dir(), "platformio.ini")) > getmtime(build_dir)):
        util.rmtree_(build_dir)

    # check project structure
    if isdir(build_dir) and isfile(structhash_file):
        with open(structhash_file) as f:
            if f.read() == proj_hash:
                return
        util.rmtree_(build_dir)

    if not isdir(build_dir):
        makedirs(build_dir)

    with open(structhash_file, "w") as f:
        f.write(proj_hash)


def print_header(label, is_error=False):
    terminal_width, _ = click.get_terminal_size()
    width = len(click.unstyle(label))
    half_line = "=" * int((terminal_width - width - 2) / 2)
    click.echo("%s %s %s" % (half_line, label, half_line), err=is_error)


def print_summary(results, start_time):
    print_header("[%s]" % click.style("SUMMARY"))

    envname_max_len = 0
    for (envname, _) in results:
        if len(envname) > envname_max_len:
            envname_max_len = len(envname)

    successed = True
    for (envname, status) in results:
        status_str = click.style("SUCCESS", fg="green")
        if status is False:
            successed = False
            status_str = click.style("ERROR", fg="red")
        elif status is None:
            status_str = click.style("SKIP", fg="yellow")

        format_str = (
            "Environment {0:<" + str(envname_max_len + 9) + "}\t[{1}]")
        click.echo(
            format_str.format(click.style(envname, fg="cyan"), status_str),
            err=status is False)

    print_header(
        "[%s] Took %.2f seconds" % (
            (click.style("SUCCESS", fg="green", bold=True) if successed else
             click.style("ERROR", fg="red", bold=True)), time() - start_time),
        is_error=not successed)


def check_project_envs(config, environments=None):  # FIXME: Remove
    if not config.sections():
        raise exception.ProjectEnvsNotAvailable()

    known = set(s[4:] for s in config.sections() if s.startswith("env:"))
    unknown = set(environments or []) - known
    if unknown:
        raise exception.UnknownEnvNames(", ".join(unknown), ", ".join(known))
    return True
