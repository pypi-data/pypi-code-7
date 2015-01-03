# -*- coding: utf-8 -*-
import os
import click

from .base import Penv


abspath = os.path.abspath
override_cd_bash_function = """
function cd () {
    builtin cd "$@" && eval "$(penv scan)"
}
"""


@click.group(invoke_without_command=True)
@click.option('--override-cd-bash', default=False, is_flag=True,
              help='Just prints the command to be evaluated by bash.')
@click.pass_context
def cli(ctx, override_cd_bash):
    if ctx.invoked_subcommand is None and override_cd_bash:
        return click.echo(override_cd_bash_function)

    if ctx.invoked_subcommand is None:
        return click.echo(ctx.command.get_help(ctx))

    # Maybe I'll make "place" customizable at some point
    ctx.obj = {
        'place': abspath('.'),
        'override_cd_bash': override_cd_bash,
    }


# $> penv [--place=/path/to/place/] scan
@cli.command('scan')
@click.pass_context
def cli_stan(ctx, env=Penv()):
    place = ctx.obj['place']
    return click.echo(env.lookup(place))
