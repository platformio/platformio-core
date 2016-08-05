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

from datetime import datetime
from hashlib import sha1
from os import getcwd, makedirs, walk
from os.path import getmtime, isdir, isfile, join
from time import time

import click

from platformio import __version__, exception, telemetry, util
from platformio.commands.lib import lib_install as cmd_lib_install
from platformio.commands.platform import \
    platform_install as cmd_platform_install
from platformio.managers.lib import LibraryManager
from platformio.managers.platform import PlatformFactory


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
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True))
@click.option("-v", "--verbose", is_flag=True)
@click.option("--disable-auto-clean", is_flag=True)
@click.pass_context
def cli(ctx,  # pylint: disable=R0913,R0914
        environment,
        target,
        upload_port,
        project_dir,
        verbose,
        disable_auto_clean):
    assert check_project_envs(project_dir, environment)
    with util.cd(project_dir):
        # clean obsolete .pioenvs dir
        if not disable_auto_clean:
            try:
                _clean_pioenvs_dir(util.get_projectpioenvs_dir())
            except:  # pylint: disable=bare-except
                click.secho(
                    "Can not remove temporary directory `%s`. Please remove "
                    "`.pioenvs` directory from the project manually to avoid "
                    "build issues" % util.get_projectpioenvs_dir(),
                    fg="yellow")

        config = util.load_project_config()
        env_default = None
        if config.has_option("platformio", "env_default"):
            env_default = [
                e.strip()
                for e in config.get("platformio", "env_default").split(",")
            ]

        results = []
        for section in config.sections():
            # skip main configuration section
            if section == "platformio":
                continue

            if not section.startswith("env:"):
                raise exception.InvalidEnvName(section)

            envname = section[4:]
            skipenv = any([environment and envname not in environment,
                           not environment and env_default and
                           envname not in env_default])
            if skipenv:
                # echo("Skipped %s environment" % style(envname, fg="yellow"))
                continue

            if results:
                click.echo()

            options = {}
            for k, v in config.items(section):
                options[k] = v
            if "piotest" not in options and "piotest" in ctx.meta:
                options['piotest'] = ctx.meta['piotest']

            ep = EnvironmentProcessor(ctx, envname, options, target,
                                      upload_port, verbose)
            results.append(ep.process())

        if not all(results):
            raise exception.ReturnErrorCode()


class EnvironmentProcessor(object):

    REMAPED_OPTIONS = {"FRAMEWORK": "PIOFRAMEWORK", "PLATFORM": "PIOPLATFORM"}

    RENAMED_OPTIONS = {
        "INSTALL_LIBS": "LIB_INSTALL",
        "IGNORE_LIBS": "LIB_IGNORE",
        "LIB_USE": "LIB_FORCE"
    }

    def __init__(self,  # pylint: disable=R0913
                 cmd_ctx,
                 name,
                 options,
                 targets,
                 upload_port,
                 verbose):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.options = self._validate_options(options)
        self.targets = targets
        self.upload_port = upload_port
        self.verbose = verbose

    def process(self):
        terminal_width, _ = click.get_terminal_size()
        start_time = time()

        click.echo("[%s] Processing %s (%s)" % (
            datetime.now().strftime("%c"), click.style(
                self.name, fg="cyan", bold=True), ", ".join(
                    ["%s: %s" % (k, v) for k, v in self.options.iteritems()])))
        click.secho("-" * terminal_width, bold=True)

        result = self._run()

        is_error = result['returncode'] != 0
        if is_error or "piotest_processor" not in self.cmd_ctx.meta:
            print_header(
                "[%s] Took %.2f seconds" % ((click.style(
                    "ERROR", fg="red", bold=True) if is_error else click.style(
                        "SUCCESS", fg="green", bold=True)),
                                            time() - start_time),
                is_error=is_error)

        return not is_error

    def _validate_options(self, options):
        result = {}
        for k, v in options.items():
            _k = k.upper()
            # process obsolete options
            if _k in self.RENAMED_OPTIONS:
                click.secho(
                    "Warning! `%s` option is deprecated and will be "
                    "removed in the next release! Please use "
                    "`%s` instead." % (k, self.RENAMED_OPTIONS[_k].lower()),
                    fg="yellow")
                k = self.RENAMED_OPTIONS[_k].lower()
            result[k] = v
        return result

    def _get_build_variables(self):
        variables = {"pioenv": self.name}
        if self.upload_port:
            variables['upload_port'] = self.upload_port
        for k, v in self.options.items():
            if k.upper() in self.REMAPED_OPTIONS:
                k = self.REMAPED_OPTIONS[k.upper()]
            k = k.lower()
            if k == "targets" or (k == "upload_port" and self.upload_port):
                continue
            variables[k] = v
        return variables

    def _get_build_targets(self):
        targets = []
        if self.targets:
            targets = [t for t in self.targets]
        elif "targets" in self.options:
            targets = self.options['targets'].split()
        return targets

    def _run(self):
        if "platform" not in self.options:
            raise exception.UndefinedEnvPlatform(self.name)

        build_vars = self._get_build_variables()
        build_targets = self._get_build_targets()

        telemetry.on_run_environment(self.options, build_targets)

        # install dependent libraries
        if "lib_install" in self.options:
            _autoinstall_libs(self.cmd_ctx, self.options['lib_install'],
                              self.verbose)

        try:
            p = PlatformFactory.newPlatform(self.options['platform'])
        except exception.UnknownPlatform:
            self.cmd_ctx.invoke(
                cmd_platform_install, platforms=[self.options['platform']])
            p = PlatformFactory.newPlatform(self.options['platform'])

        return p.run(build_vars, build_targets, self.verbose)


def _autoinstall_libs(ctx, libids_list, verbose=False):
    storage_dir = util.get_projectlibdeps_dir()
    ctx.obj = LibraryManager(storage_dir)
    if verbose:
        click.echo("Library Storage: " + storage_dir)
    ctx.invoke(
        cmd_lib_install,
        libraries=[int(l.strip()) for l in libids_list.split(",")],
        quiet=not verbose)


def _clean_pioenvs_dir(pioenvs_dir):
    structhash_file = join(pioenvs_dir, "structure.hash")
    proj_hash = calculate_project_hash()

    # if project's config is modified
    if (isdir(pioenvs_dir) and
            getmtime(join(util.get_project_dir(), "platformio.ini")) >
            getmtime(pioenvs_dir)):
        util.rmtree_(pioenvs_dir)

    # check project structure
    if isdir(pioenvs_dir) and isfile(structhash_file):
        with open(structhash_file) as f:
            if f.read() == proj_hash:
                return
        util.rmtree_(pioenvs_dir)

    if not isdir(pioenvs_dir):
        makedirs(pioenvs_dir)

    with open(structhash_file, "w") as f:
        f.write(proj_hash)


def print_header(label, is_error=False):
    terminal_width, _ = click.get_terminal_size()
    width = len(click.unstyle(label))
    half_line = "=" * ((terminal_width - width - 2) / 2)
    click.echo("%s %s %s" % (half_line, label, half_line), err=is_error)


def check_project_envs(project_dir, environments):
    config = util.load_project_config(project_dir)

    if not config.sections():
        raise exception.ProjectEnvsNotAvailable()

    known = set([s[4:] for s in config.sections() if s.startswith("env:")])
    unknown = set(environments) - known
    if unknown:
        raise exception.UnknownEnvNames(", ".join(unknown), ", ".join(known))
    return True


def calculate_project_hash():
    structure = [__version__]
    for d in (util.get_projectsrc_dir(), util.get_projectlib_dir()):
        if not isdir(d):
            continue
        for root, _, files in walk(d):
            for f in files:
                path = join(root, f)
                if not any([s in path for s in (".git", ".svn", ".pioenvs")]):
                    structure.append(path)
    return sha1(",".join(sorted(structure))).hexdigest() if structure else ""
