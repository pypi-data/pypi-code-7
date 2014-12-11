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
    _cur_x, _cur_y, _cur_z = _last_build_number.split('.')

    if not bugfix:
        if days_since_epoch == _cur_x:
            _cur_y = int(_cur_y) + 1
        else:
            _cur_x = days_since_epoch
            _cur_y = 0
    else:
        _cur_z = int(_cur_z) + 1

    return '.'.join([str(_cur_x), str(_cur_y), str(_cur_z)])


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
