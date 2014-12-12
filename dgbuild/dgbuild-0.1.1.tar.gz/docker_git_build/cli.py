import sys
import ConfigParser
import datetime
import subprocess

import click
from termcolor import colored
import git


epoch = None
docker_repo = None
rcfile = '.dgbuildrc'


def info(message):
    print colored('[INFO] %s' % message, 'green')


def warn(message):
    print colored('[WARN] %s' % message, 'yellow')


def error(message):
    print colored('[ERROR] %s' % message, 'red')
    sys.exit(-1)


def last_build_number(repo):
    description = repo.git.describe()
    try:
        tag, commits, githash = description.split('-')
    except:
        tag = description
    return tag


def determine_next_build_number(repo, epoch, bugfix=False):
    days_since_epoch = datetime.date.today() - epoch.date()
    days_since_epoch = days_since_epoch.days

    _last_build_number = last_build_number(repo)
    _version = [int(i) for i in _last_build_number.split('.')]

    _new_x, _new_y, _new_z = 0, 0, 0

    if not bugfix:
        # not bugfixing, so new build will be x = today
        _new_x = days_since_epoch

        if days_since_epoch == _version[0]:
            # previous builds exist today
            warn('same day as last build.')
            _new_y = _version[1] + 1
        else:
            _new_y = 0
            _new_z = 0
    else:
        _new_x, _new_y, _new_z = _version[0], _version[1], _version[2] + 1

    return '.'.join([str(_new_x), str(_new_y), str(_new_z)])


def read_config():
    # parse config
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(rcfile))
    except Exception, e:
        error("Config file not found or contains error: {}".format(e))
    section_name = 'Docker Build'
    try:
        options = config.options(section_name)
        if 'docker_repo' in options:
            docker_repo = config.get(section_name, 'docker_repo')
        if 'epoch' in options:
            _epoch = config.get(section_name, 'epoch')
            epoch = datetime.datetime.strptime(_epoch, '%m/%d/%Y')

        return [epoch, docker_repo]
    except Exception, e:
        error(e)


@click.command()
@click.option('--bugfix/--no-bugfix',
              default=False,
              required=False)
def build(bugfix):
    epoch = None
    docker_repo = None
    epoch, docker_repo = read_config()
    repo = git.repo.Repo('.')
    next_build_number = determine_next_build_number(repo, epoch, bugfix)
    docker_remote = '{}:{}'.format(docker_repo, next_build_number)
    info('Proposed build id: {}'.format(next_build_number))
    info('The last 10 commits at this head are:')
    for line in repo.git.log('--pretty=oneline').splitlines()[:10]:
        print line
    if click.confirm('Build {}'.format(next_build_number)):
        subprocess.call(['docker',
                         'build',
                         '-t',
                         '{}'.format(docker_remote),
                         '.'])
        if click.confirm('Push to docker hub and github?'):
            subprocess.call(['docker', 'push', '{}'.format(docker_remote)])
            repo.create_tag(next_build_number, message=next_build_number)
            repo.remote('origin').push()


if __name__ == '__main__':
    build()
