import os
import logging
import pkg_resources

from docopt import docopt

import utils
from nb import NotaBene

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-16s %(lineno)3s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='nb.log',
                    filemode='a')

HELP="""Nota Bene

Usage:
    nb init
    nb add <filename>...
    nb rm <filename>...
    nb list
    nb tag [-i | -u] <tag>...
    nb (-h | --help)
    nb --version

Options:
    -h --help           Show this screen
    --version           Show version information
    -i --intersection   List the intersection of tags
    -u --union          List the union of tags (default)
"""
version = pkg_resources.require("nb")[0].version


def _nb_or_exit(nb_dir):
    try:
        nb = utils.get_nb_from_nb_dir(nb_dir)
        return nb
    except Exception as e:
        log.error(e)
        exit(-1)


def main():
    cwd = os.getcwd()
    log.debug('In {}'.format(cwd))
    nb_dir, nb_root = utils.search_nb_dir(cwd)
    opt = docopt(HELP, version=version)

    if opt['add']:
        files = opt['<filename>']

        nb = _nb_or_exit(nb_dir)

        for f in files:
            fpath = os.path.join(cwd, f)
            if os.path.isfile(fpath):
                    log.debug('Adding {}'.format(fpath))
                    nb.add_note(fpath, nb_root)
                    print('{} added'.format(fpath))
                    utils.store(nb_dir, nb)

    elif opt['list']:
        nb = _nb_or_exit(nb_dir)

        for n in nb.file_list():
            print(n)

    elif opt['tag']:
        nb = _nb_or_exit(nb_dir)
        tags = opt['<tag>']
        if opt['--intersection']:
            try:
                for n in nb.tag_intersection(tags):
                    print(n)
            except Exception as e:
                log.error(e)
        else:
            try:
                for n in nb.tag_union(tags):
                    print(n)
            except Exception as e:
                log.error(e)

    elif opt['rm']:
        files = opt['<filename>']

        nb = _nb_or_exit(nb_dir)

        for f in files:
            fpath = os.path.join(cwd, f)

            log.debug('Removing {}'.format(fpath))
            nb.rm_note(fpath, nb_root)
            print('{} removed'.format(fpath))
            utils.store(nb_dir, nb)

    elif opt['init']:
        if nb_dir:
            log.error('Nota Bene already inizialized at {}'.format(nb_dir))
            exit(-1)
        else:
            print('Initializing Nota Bene in {}'.format(cwd))
            try:
                nb_dir = utils.create_nb_dir(cwd)
            except Exception as e:
                log.error(e)
                exit(-1)

            nb = NotaBene()
            log.debug('Dumping initial database')
            utils.store(nb_dir, nb)

