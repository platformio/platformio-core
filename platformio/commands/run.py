# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, option, secho, style

from platformio import telemetry
from platformio.exception import (InvalidEnvName, ProjectEnvsNotAvaialable,
                                  UndefinedEnvPlatform, UnknownEnvNames)
from platformio.platforms.base import PlatformFactory
from platformio.util import get_project_config


@command("run", short_help="Process project environments")
@option("--environment", "-e", multiple=True, metavar="<environment>")
@option("--target", "-t", multiple=True, metavar="<target>")
@option("--upload-port", metavar="<upload port>")
def cli(environment, target, upload_port):

    config = get_project_config()

    if not config.sections():
        raise ProjectEnvsNotAvaialable()

    unknown = set(environment) - set([s[4:] for s in config.sections()])
    if unknown:
        raise UnknownEnvNames(", ".join(unknown))

    for section in config.sections():
        # skip main configuration section
        if section == "platformio":
            continue
        elif section[:4] != "env:":
            raise InvalidEnvName(section)

        envname = section[4:]
        if environment and envname not in environment:
            # echo("Skipped %s environment" % style(envname, fg="yellow"))
            continue

        echo("Processing %s environment:" % style(envname, fg="cyan"))

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
            raise UndefinedEnvPlatform(envname)

        telemetry.on_run_environment(config.items(section), envtargets)

        p = PlatformFactory().newPlatform(config.get(section, "platform"))
        result = p.run(variables, envtargets)
        secho(result['out'], fg="green")
        secho(result['err'],
              fg="red" if "Error" in result['err'] else "yellow")
