# c/p from https://github.com/click-contrib/click-completion/blob/master/examples/click-completion-command

import click
import click_completion
import click_completion.core

@click.group("completion", short_help="Manage shell completions")
def cli():
    pass

@cli.command("show", short_help="Show shell command code")
@click.option('-i', '--case-insensitive/--no-case-insensitive', help="Case insensitive completion")
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
def completion_show(shell, case_insensitive):
    """Show the click-completion-command completion code"""
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    click.echo(click_completion.core.get_code(shell, extra_env=extra_env))


@cli.command("install", short_help="Install shell completion files")
@click.option('--append/--overwrite', help="Append the completion code to the file", default=None)
@click.option('-i', '--case-insensitive/--no-case-insensitive', help="Case insensitive completion")
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument('path', required=False)
def completion_install(append, case_insensitive, shell, path):
    """Install the click-completion-command completion"""
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    shell, path = click_completion.core.install(shell=shell, path=path, append=append, extra_env=extra_env)
    click.echo('%s completion installed in %s' % (shell, path))
