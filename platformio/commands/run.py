# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from datetime import datetime
from hashlib import sha1
from os import getcwd, makedirs, walk
from os.path import getmtime, isdir, isfile, join
from shutil import rmtree
from time import time

import click

from platformio import app, exception, telemetry, util
from platformio.commands.lib import lib_install as cmd_lib_install
from platformio.commands.platforms import \
    platforms_install as cmd_platforms_install
from platformio.libmanager import LibraryManager
from platformio.platforms.base import PlatformFactory


@click.command("run", short_help="Process project environments")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option("--target", "-t", multiple=True, metavar="<target>")
@click.option("--upload-port", metavar="<upload port>")
@click.option("--project-dir", "-d", default=getcwd,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.option("--verbose", "-v", count=True, default=3)
@click.option("--disable-auto-clean", is_flag=True)
@click.pass_context
def cli(ctx, environment, target, upload_port,  # pylint: disable=R0913,R0914
        project_dir, verbose, disable_auto_clean):
    with util.cd(project_dir):
        config = util.get_project_config()

        if not config.sections():
            raise exception.ProjectEnvsNotAvailable()

        unknown = set(environment) - set([s[4:] for s in config.sections()])
        if unknown:
            raise exception.UnknownEnvNames(", ".join(unknown))

        # clean obsolete .pioenvs dir
        if not disable_auto_clean:
            _clean_pioenvs_dir()

        results = []
        for section in config.sections():
            # skip main configuration section
            if section == "platformio":
                continue

            if not section.startswith("env:"):
                raise exception.InvalidEnvName(section)

            envname = section[4:]
            if environment and envname not in environment:
                # echo("Skipped %s environment" % style(envname, fg="yellow"))
                continue

            if results:
                click.echo()

            options = {}
            for k, v in config.items(section):
                options[k] = v

            ep = EnvironmentProcessor(
                ctx, envname, options, target, upload_port, verbose)
            results.append(ep.process())

        if not all(results):
            raise exception.ReturnErrorCode()


class EnvironmentProcessor(object):

    RENAMED_OPTIONS = {
        "INSTALL_LIBS": "LIB_INSTALL",
        "IGNORE_LIBS": "LIB_IGNORE",
        "USE_LIBS": "LIB_USE",
        "LDF_CYCLIC": "LIB_DFCYCLIC",
        "SRCBUILD_FLAGS": "SRC_BUILD_FLAGS"
    }

    def __init__(self, cmd_ctx, name, options,  # pylint: disable=R0913
                 targets, upload_port, verbose):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.options = self._validate_options(options)
        self.targets = targets
        self.upload_port = upload_port
        self.verbose_level = int(verbose)

    def process(self):
        terminal_width, _ = click.get_terminal_size()
        start_time = time()

        click.echo("[%s] Processing %s (%s)" % (
            datetime.now().strftime("%c"),
            click.style(self.name, fg="cyan", bold=True),
            ", ".join(["%s: %s" % (k, v) for k, v in self.options.iteritems()])
        ))
        click.secho("-" * terminal_width, bold=True)

        result = self._run()

        is_error = result['returncode'] != 0
        summary_text = " Took %.2f seconds " % (time() - start_time)
        half_line = "=" * ((terminal_width - len(summary_text) - 10) / 2)
        click.echo("%s [%s]%s%s" % (
            half_line,
            (click.style(" ERROR ", fg="red", bold=True)
             if is_error else click.style("SUCCESS", fg="green", bold=True)),
            summary_text,
            half_line
        ), err=is_error)

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
                    "`%s` instead." % (
                        k, self.RENAMED_OPTIONS[_k].lower()),
                    fg="yellow"
                )
                k = self.RENAMED_OPTIONS[_k].lower()
            result[k] = v
        return result

    def _get_build_variables(self):
        variables = ["PIOENV=" + self.name]
        if self.upload_port:
            variables.append("UPLOAD_PORT=%s" % self.upload_port)
        for k, v in self.options.items():
            k = k.upper()
            if k == "TARGETS" or (k == "UPLOAD_PORT" and self.upload_port):
                continue
            variables.append("%s=%s" % (k, v))
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

        platform = self.options['platform']
        build_vars = self._get_build_variables()
        build_targets = self._get_build_targets()

        telemetry.on_run_environment(self.options, build_targets)

        # install platform and libs dependencies
        _autoinstall_platform(self.cmd_ctx, platform, build_targets)
        if "lib_install" in self.options:
            _autoinstall_libs(self.cmd_ctx, self.options['lib_install'])

        p = PlatformFactory.newPlatform(platform)
        return p.run(build_vars, build_targets, self.verbose_level)


def _autoinstall_platform(ctx, platform, targets):
    installed_platforms = PlatformFactory.get_platforms(installed=True).keys()
    cmd_options = {}
    p = PlatformFactory.newPlatform(platform)

    if "uploadlazy" in targets:
        upload_tools = p.pkg_aliases_to_names(["uploader"])

        # platform without uploaders
        if not upload_tools and platform in installed_platforms:
            return
        # uploaders are already installed
        if set(upload_tools) <= set(p.get_installed_packages()):
            return

        cmd_options['skip_default_package'] = True
        if upload_tools:
            cmd_options['with_package'] = ["uploader"]

    elif (platform in installed_platforms and
          set(p.get_default_packages()) <= set(p.get_installed_packages())):
        return

    if (not app.get_setting("enable_prompts") or
            click.confirm("The platform '%s' has not been installed yet. "
                          "Would you like to install it now?" % platform)):
        ctx.invoke(cmd_platforms_install, platforms=[platform], **cmd_options)


def _autoinstall_libs(ctx, libids_list):
    require_libs = [int(l.strip()) for l in libids_list.split(",")]
    installed_libs = [
        l['id'] for l in LibraryManager().get_installed().values()
    ]

    not_intalled_libs = set(require_libs) - set(installed_libs)
    if not require_libs or not not_intalled_libs:
        return

    if (not app.get_setting("enable_prompts") or
            click.confirm(
                "The libraries with IDs '%s' have not been installed yet. "
                "Would you like to install them now?" %
                ", ".join([str(i) for i in not_intalled_libs])
            )):
        ctx.invoke(cmd_lib_install, libid=not_intalled_libs)


def _clean_pioenvs_dir():
    pioenvs_dir = util.get_pioenvs_dir()
    structhash_file = join(pioenvs_dir, "structure.hash")
    proj_hash = calculate_project_hash()

    # if project's config is modified
    if (isdir(pioenvs_dir) and
            getmtime(join(util.get_project_dir(), "platformio.ini")) >
            getmtime(pioenvs_dir)):
        rmtree(pioenvs_dir)

    # check project structure
    if isdir(pioenvs_dir) and isfile(structhash_file):
        with open(structhash_file) as f:
            if f.read() == proj_hash:
                return
        rmtree(pioenvs_dir)

    if not isdir(pioenvs_dir):
        makedirs(pioenvs_dir)

    with open(structhash_file, "w") as f:
        f.write(proj_hash)


def calculate_project_hash():
    structure = []
    for d in (util.get_projectsrc_dir(), util.get_projectlib_dir()):
        if not isdir(d):
            continue
        for root, _, files in walk(d):
            for f in files:
                path = join(root, f)
                if not any([s in path for s in (".git", ".svn")]):
                    structure.append(path)
    return sha1(",".join(sorted(structure))).hexdigest() if structure else ""
