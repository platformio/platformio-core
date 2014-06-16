# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, option, secho, style

from platformio.exception import ProjectEnvsNotAvaialable, UndefinedEnvPlatform
from platformio.platforms._base import PlatformFactory
from platformio.util import get_project_config


@command("run", short_help="Process project environments")
@option("--environment", "-e", multiple=True, metavar="<environment>")
@option("--target", "-t", multiple=True, metavar="<target>")
def cli(environment, target):

    config = get_project_config()

    if not config.sections():
        raise ProjectEnvsNotAvaialable()

    for section in config.sections():
        if section[:4] != "env:":
            continue

        envname = section[4:]
        if environment and envname not in environment:
            echo("Skipped %s environment" % style(envname, fg="yellow"))
            continue

        echo("Processing %s environment:" % style(envname, fg="cyan"))
        variables = ["%s=%s" % (o.upper(), v) for o, v in config.items(section)
                     if o != "targets"]
        variables.append("PIOENV=" + envname)

        envtargets = []
        if target:
            envtargets = [t for t in target]
        elif config.has_option(section, "targets"):
            envtargets = config.get(section, "targets").split()

        if not config.has_option(section, "platform"):
            raise UndefinedEnvPlatform(envname)

        p = PlatformFactory().newPlatform(config.get(section, "platform"))
        result = p.run(variables, envtargets)
        secho(result['out'], fg="green")
        secho(result['err'], fg="red")
