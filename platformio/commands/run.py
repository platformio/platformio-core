# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from datetime import datetime
from os import chdir, getcwd
from os.path import getmtime, isdir, join
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
@click.option("--project-dir", default=getcwd,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True))
@click.pass_context
def cli(ctx, environment, target, upload_port, project_dir):
    initial_cwd = getcwd()
    chdir(project_dir)
    try:
        config = util.get_project_config()

        if not config.sections():
            raise exception.ProjectEnvsNotAvailable()

        unknown = set(environment) - set([s[4:] for s in config.sections()])
        if unknown:
            raise exception.UnknownEnvNames(", ".join(unknown))

        # remove ".pioenvs" if project config is modified
        _pioenvs_dir = util.get_pioenvs_dir()
        if (isdir(_pioenvs_dir) and
                getmtime(join(util.get_project_dir(), "platformio.ini")) >
                getmtime(_pioenvs_dir)):
            rmtree(_pioenvs_dir)

        results = []
        for section in config.sections():
            if results and results[-1] is not None:
                click.echo()

            results.append(_process_conf_section(
                ctx, config, section, environment, target, upload_port))

        if not all([r for r in results if r is not None]):
            raise exception.ReturnErrorCode()
    finally:
        chdir(initial_cwd)


def _process_conf_section(ctx, config, section,  # pylint: disable=R0913
                          environment, target, upload_port):
    # skip main configuration section
    if section == "platformio":
        return None

    if section[:4] != "env:":
        raise exception.InvalidEnvName(section)

    envname = section[4:]
    if environment and envname not in environment:
        # echo("Skipped %s environment" % style(envname, fg="yellow"))
        return None

    options = {}
    for k, v in config.items(section):
        options[k] = v

    return _process_environment(ctx, envname, options, target, upload_port)


def _process_environment(ctx, name, options, targets, upload_port):
    terminal_width, _ = click.get_terminal_size()
    start_time = time()

    click.echo("[%s] Processing %s (%s)" % (
        datetime.now().strftime("%c"),
        click.style(name, fg="cyan", bold=True),
        ", ".join(["%s: %s" % (k, v) for k, v in options.iteritems()])
    ))
    click.secho("-" * terminal_width, bold=True)

    result = _run_environment(ctx, name, options, targets, upload_port)

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


def _run_environment(ctx, name, options, targets, upload_port):
    variables = ["PIOENV=" + name]
    if upload_port:
        variables.append("UPLOAD_PORT=%s" % upload_port)
    for k, v in options.items():
        k = k.upper()
        if k == "TARGETS" or (k == "UPLOAD_PORT" and upload_port):
            continue
        variables.append("%s=%s" % (k.upper(), v))

    envtargets = []
    if targets:
        envtargets = [t for t in targets]
    elif "targets" in options:
        envtargets = options['targets'].split()

    if "platform" not in options:
        raise exception.UndefinedEnvPlatform(name)
    platform = options['platform']

    telemetry.on_run_environment(options, envtargets)

    # install platform and libs dependencies
    _autoinstall_env_platform(ctx, platform)
    if "install_libs" in options:
        _autoinstall_env_libs(ctx, options['install_libs'])

    p = PlatformFactory.newPlatform(platform)
    return p.run(variables, envtargets)


def _autoinstall_env_platform(ctx, platform):
    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    if (platform not in installed_platforms and (
            not app.get_setting("enable_prompts") or
            click.confirm("The platform '%s' has not been installed yet. "
                          "Would you like to install it now?" % platform))):
        ctx.invoke(cmd_platforms_install, platforms=[platform])


def _autoinstall_env_libs(ctx, libids_list):
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
