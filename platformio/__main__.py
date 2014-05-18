# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click
from sys import exit

from clint.textui import colored, indent, puts


from platformio.util import get_project_config, run_builder


@click.group()
def main():
    pass


@main.group()
def init():
    """ Initialize new platformio based project """
    pass


@main.group()
def install():
    """ Install new platforms """
    pass


@main.group()
def list():
    """ List installed platforms  """
    pass


@main.command()
@click.option("--environment", "-e", multiple=True)
@click.option("--target", "-t", multiple=True)
def run(environment, target):
    """Process project environments """

    config = get_project_config()
    for section in config.sections():
        if section[:4] != "env:":
            continue
        envname = section[4:]

        if environment and envname not in environment:
            puts("Skipped %s environment" % colored.yellow(envname))
            continue

        puts("Processing %s environment:" % colored.cyan(envname))
        variables = ["%s=%s" % (o.upper(), v) for o, v in config.items(section)
                     if o != "targets"]
        variables.append("PIOENV=" + envname)

        envtargets = []
        if target:
            envtargets = [t for t in target]
        elif config.has_option(section, "targets"):
            envtargets = config.get(section, "targets").split()

        result = run_builder(variables, envtargets)

        # print result
        with indent(4, quote=colored.white(".")):
            puts(colored.green(result['out']))
            puts(colored.red(result['err']))


@main.group()
def search():
    """ Search for new platforms """
    pass


@main.group()
def show():
    """ Show information about installed platforms  """
    pass


if __name__ == "__main__":
    exit(main())
