import os
import fnmatch
import ConfigParser
from subprocess import call

import click

import tagutils


def find_registered_repos(directory):

    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '.pymr'):
            matches.append(os.path.join(root, filename))

    return matches


def find_tagged_files(files, tag):

    matches = []
    for fn in files:
        config = ConfigParser.ConfigParser()
        config.readfp(open(fn))

        tags = config.get('tags', 'tags')
        tag_list = tagutils.unpack(tags)

        for t in [tag]:
            if t in tag_list:
                matches.append(fn)

    return matches


def run_command(match_files, command):
    for fn in match_files:
        print 'calling {0} in {1}'.format(command, fn)
        os.chdir(os.path.dirname(fn))
        call(command, shell=True)


@click.command()
@click.argument('command')
@click.option('--tag', '-t', multiple=True)
@click.option('--dryrun', '-d', is_flag=True)
@click.option('--basepath', '-b', default='./')
def run(command, tag, dryrun, basepath):
    """
    run a command on registered directories
    """
    tag = tagutils.set_default(tag)
    tag = tagutils.parse(tag)
    files = find_registered_repos(basepath)
    match_files = find_tagged_files(files, tag)

    if dryrun:
        for fn in match_files:
            print 'would run {0} in {1}'.format(command, fn)
    else:
        run_command(match_files, command)
