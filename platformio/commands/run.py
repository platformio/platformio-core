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

from hashlib import sha1
from os import getcwd, makedirs, walk
from os.path import getmtime, isdir, isfile, join
from time import time

import click

from platformio import __version__, exception, telemetry, util
from platformio.commands.device import device_monitor as cmd_device_monitor
from platformio.commands.lib import lib_install as cmd_lib_install
from platformio.commands.platform import \
    platform_install as cmd_platform_install
from platformio.managers.lib import LibraryManager, is_builtin_lib
from platformio.managers.platform import PlatformFactory

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
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--disable-auto-clean", is_flag=True)
@click.pass_context
def cli(ctx, environment, target, upload_port, project_dir, silent, verbose,
        disable_auto_clean):
    # find project directory on upper level
    if isfile(project_dir):
        project_dir = util.find_project_dir_above(project_dir)

    if not util.is_platformio_project(project_dir):
        raise exception.NotPlatformIOProject(project_dir)

    with util.cd(project_dir):
        # clean obsolete build dir
        if not disable_auto_clean:
            try:
                _clean_build_dir(util.get_projectbuild_dir())
            except:  # pylint: disable=bare-except
                click.secho(
                    "Can not remove temporary directory `%s`. Please remove "
                    "it manually to avoid build issues" %
                    util.get_projectbuild_dir(force=True),
                    fg="yellow")

        config = util.load_project_config()
        env_default = None
        if config.has_option("platformio", "env_default"):
            env_default = util.parse_conf_multi_values(
                config.get("platformio", "env_default"))

        check_project_defopts(config)
        check_project_envs(config, environment or env_default)

        results = []
        start_time = time()
        for section in config.sections():
            if not section.startswith("env:"):
                continue

            envname = section[4:]
            skipenv = any([
                environment and envname not in environment, not environment
                and env_default and envname not in env_default
            ])
            if skipenv:
                results.append((envname, None))
                continue

            if not silent and results:
                click.echo()

            options = {}
            for k, v in config.items(section):
                options[k] = v
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

    KNOWN_PLATFORMIO_OPTIONS = [
        "description", "env_default", "home_dir", "lib_dir", "libdeps_dir",
        "include_dir", "src_dir", "build_dir", "data_dir", "test_dir",
        "boards_dir", "lib_extra_dirs"
    ]

    KNOWN_ENV_OPTIONS = [
        "platform", "framework", "board", "build_flags", "src_build_flags",
        "build_unflags", "src_filter", "extra_scripts", "targets",
        "upload_port", "upload_protocol", "upload_speed", "upload_flags",
        "upload_resetmethod", "lib_deps", "lib_ignore", "lib_extra_dirs",
        "lib_ldf_mode", "lib_compat_mode", "lib_archive", "piotest",
        "test_transport", "test_filter", "test_ignore", "test_port",
        "test_speed", "test_build_project_src", "debug_tool", "debug_port",
        "debug_init_cmds", "debug_extra_cmds", "debug_server",
        "debug_init_break", "debug_load_cmd", "debug_load_mode",
        "debug_svd_path", "monitor_port", "monitor_speed", "monitor_rts",
        "monitor_dtr"
    ]

    IGNORE_BUILD_OPTIONS = [
        "test_transport", "test_filter", "test_ignore", "test_port",
        "test_speed", "debug_port", "debug_init_cmds", "debug_extra_cmds",
        "debug_server", "debug_init_break", "debug_load_cmd",
        "debug_load_mode", "monitor_port", "monitor_speed", "monitor_rts",
        "monitor_dtr"
    ]

    REMAPED_OPTIONS = {"framework": "pioframework", "platform": "pioplatform"}

    RENAMED_OPTIONS = {
        "lib_use": "lib_deps",
        "lib_force": "lib_deps",
        "extra_script": "extra_scripts",
        "monitor_baud": "monitor_speed",
        "board_mcu": "board_build.mcu",
        "board_f_cpu": "board_build.f_cpu",
        "board_f_flash": "board_build.f_flash",
        "board_flash_mode": "board_build.flash_mode"
    }

    RENAMED_PLATFORMS = {"espressif": "espressif8266"}

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

        self.options = self._validate_options(self.options)
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

    def _validate_options(self, options):
        result = {}
        for k, v in options.items():
            # process obsolete options
            if k in self.RENAMED_OPTIONS:
                click.secho(
                    "Warning! `%s` option is deprecated and will be "
                    "removed in the next release! Please use "
                    "`%s` instead." % (k, self.RENAMED_OPTIONS[k]),
                    fg="yellow")
                k = self.RENAMED_OPTIONS[k]
            # process renamed platforms
            if k == "platform" and v in self.RENAMED_PLATFORMS:
                click.secho(
                    "Warning! Platform `%s` is deprecated and will be "
                    "removed in the next release! Please use "
                    "`%s` instead." % (v, self.RENAMED_PLATFORMS[v]),
                    fg="yellow")
                v = self.RENAMED_PLATFORMS[v]

            # warn about unknown options
            unknown_conditions = [
                k not in self.KNOWN_ENV_OPTIONS, not k.startswith("custom_"),
                not k.startswith("board_")
            ]
            if all(unknown_conditions):
                click.secho(
                    "Detected non-PlatformIO `%s` option in `[env:%s]` section"
                    % (k, self.name),
                    fg="yellow")
            result[k] = v
        return result

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
    storage_dir = util.get_projectlibdeps_dir()
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
    if (isdir(build_dir)
            and getmtime(join(util.get_project_dir(),
                              "platformio.ini")) > getmtime(build_dir)):
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
    half_line = "=" * ((terminal_width - width - 2) / 2)
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


def check_project_defopts(config):
    if not config.has_section("platformio"):
        return True
    unknown = set([k for k, _ in config.items("platformio")]) - set(
        EnvironmentProcessor.KNOWN_PLATFORMIO_OPTIONS)
    if not unknown:
        return True
    click.secho(
        "Warning! Ignore unknown `%s` option in `[platformio]` section" %
        ", ".join(unknown),
        fg="yellow")
    return False


def check_project_envs(config, environments=None):
    if not config.sections():
        raise exception.ProjectEnvsNotAvailable()

    known = set([s[4:] for s in config.sections() if s.startswith("env:")])
    unknown = set(environments or []) - known
    if unknown:
        raise exception.UnknownEnvNames(", ".join(unknown), ", ".join(known))
    return True


def calculate_project_hash():
    check_suffixes = (".c", ".cc", ".cpp", ".h", ".hpp", ".s", ".S")
    chunks = [__version__]
    for d in (util.get_projectsrc_dir(), util.get_projectlib_dir()):
        if not isdir(d):
            continue
        for root, _, files in walk(d):
            for f in files:
                path = join(root, f)
                if path.endswith(check_suffixes):
                    chunks.append(path)
    chunks_to_str = ",".join(sorted(chunks))
    if "windows" in util.get_systype():
        # Fix issue with useless project rebuilding for case insensitive FS.
        # A case of disk drive can differ...
        chunks_to_str = chunks_to_str.lower()
    return sha1(chunks_to_str).hexdigest()
