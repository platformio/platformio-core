# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, option, style

from platformio.util import get_project_config, run_builder, textindent


@command("run", short_help="Process project environments")
@option("--environment", "-e", multiple=True)
@option("--target", "-t", multiple=True)
def cli(environment, target):
    config = get_project_config()
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

        result = run_builder(variables, envtargets)
        echo(textindent(style(result['out'], fg="green"), ".    "))
        echo(textindent(style(result['err'], fg="red"), ".    "))
