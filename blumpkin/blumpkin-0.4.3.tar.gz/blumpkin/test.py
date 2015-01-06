from __future__ import unicode_literals
import sys

import click
import pytest
import subprocess


@click.command('test')
@click.option('--cov')
@click.option('--cov-report', nargs=2)
@click.argument('target')
def test(cov, cov_report, target):
    sys.exit(run(cov, cov_report, target))


def run(cov, cov_report, target):
    args = ['py.test']
    args.append('-p cov')
    if cov:
        args.append('--cov=' + cov)
    for report in cov_report:
        args.append('--cov-report')
        args.append(report)
    if target:
        args.append(target)
    return subprocess.call(args)
