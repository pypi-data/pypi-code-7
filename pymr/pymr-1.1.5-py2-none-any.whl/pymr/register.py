import os
import warnings
import ConfigParser

import click

import tagutils


def create_config(tag):
    config = ConfigParser.RawConfigParser()
    config.add_section('tags')
    config.set('tags', 'tags', tag)

    return config


def append_tags(config, tag):
    if not config.has_section('tags'):
        config.add_section('tags')

    tags = config.get('tags', 'tags')
    tag_list = tagutils.unpack(tags)

    for t in [tag]:
        if t not in tag_list:
            tag_list.append(t)

    tag = tagutils.parse(tag_list)
    config.set('tags', 'tags', tag)

    return config


def get_config(directory, tag, append):
    if append:
        fn = os.path.join(directory, '.pymr')
        if os.path.exists(fn):
            config = ConfigParser.ConfigParser()
            config.readfp(open(fn))
            config = append_tags(config, tag)
    else:
        config = create_config(tag)

    return config


def create_config_file(directory):
    fid = open(os.path.join(directory, '.pymr'), 'w')

    return fid


def write_config_to_file(fid, config):
    config.write(fid)
    fid.close()


@click.command()
@click.option('--directory', '-d', default='./')
@click.option('--tag', '-t', multiple=True)
@click.option('--append', is_flag=True)
def register(directory, tag, append):
    """
    register a directory for use with pymr \n
    example: pymr-register -d ./ -t foo -t bar
    """
    print 'Creating file .pymr in {0}'.format(directory)

    tag = tagutils.set_default(tag)
    tag = tagutils.parse(tag)
    config = get_config(directory, tag, append)
    fid = create_config_file(directory)
    write_config_to_file(fid, config)
