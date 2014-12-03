# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio import exception, telemetry
from platformio.commands.install import cli as cmd_install
from platformio.platforms.base import PlatformFactory
from platformio.util import get_project_config


@click.command("run", short_help="Process project environments")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option("--target", "-t", multiple=True, metavar="<target>")
@click.option("--upload-port", metavar="<upload port>")
@click.pass_context
def cli(ctx, environment, target, upload_port):

    config = get_project_config()

    if not config.sections():
        raise exception.ProjectEnvsNotAvaialable()

    unknown = set(environment) - set([s[4:] for s in config.sections()])
    if unknown:
        raise exception.UnknownEnvNames(", ".join(unknown))

    for section in config.sections():
        # skip main configuration section
        if section == "platformio":
            continue
        elif section[:4] != "env:":
            raise exception.InvalidEnvName(section)

        envname = section[4:]
        if environment and envname not in environment:
            # echo("Skipped %s environment" % style(envname, fg="yellow"))
            continue

        click.echo("Processing %s environment:" %
                   click.style(envname, fg="cyan"))

        variables = ["PIOENV=" + envname]
        if upload_port:
            variables.append("UPLOAD_PORT=%s" % upload_port)
        for k, v in config.items(section):
            k = k.upper()
            if k == "TARGETS" or (k == "UPLOAD_PORT" and upload_port):
                continue
            variables.append("%s=%s" % (k.upper(), v))

        envtargets = []
        if target:
            envtargets = [t for t in target]
        elif config.has_option(section, "targets"):
            envtargets = config.get(section, "targets").split()

        if not config.has_option(section, "platform"):
            raise exception.UndefinedEnvPlatform(envname)
        platform = config.get(section, "platform")

        telemetry.on_run_environment(config.items(section), envtargets)

        if (platform not in PlatformFactory.get_platforms(installed=True) and
                click.confirm("The platform '%s' has not been installed yet. "
                              "Would you like to install it now?" % platform)):
            ctx.invoke(cmd_install, platforms=[platform])

        p = PlatformFactory.newPlatform(platform)
        result = p.run(variables, envtargets)
        click.secho(result['out'], fg="green")
        click.secho(result['err'],
                    fg="red" if "Error" in result['err'] else "yellow")
