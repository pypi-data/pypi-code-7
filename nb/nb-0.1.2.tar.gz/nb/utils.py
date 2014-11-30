import os
import logging
import pickle
import datetime

import yaml

log = logging.getLogger(__name__)

class Note(object):
    def __init__(self, fpath, title='Untitled', tags=[]):
        self.title = title
        self.tags = tags
        self.filepath = fpath
        self.date = datetime.datetime.now()

    def set_date(self, d):
        self.date = d

    def __str__(self):
        return '{:<40}{:<50}{}'.format(self.filepath, self.title.encode('utf8'), ','.join(t for t in self.tags).encode('utf8'))

FOLDER_NAME = '.nb'
def search_nb_dir(cwd):
    rel = '.'
    while True:
        pardir = os.path.abspath(os.path.join(cwd, rel))
        nb_dir = os.path.join(pardir, FOLDER_NAME)
        log.debug('Checking {} for root'.format(pardir))
        if os.path.isdir(os.path.join(nb_dir)):
            return nb_dir, pardir
        else:
            log.debug('Nota Bene root not found in {}'.format(rel))
            if pardir == os.path.abspath(os.sep):
                return None, None
            rel = os.path.join(rel, '..')


def get_note_from_file(filepath, nb_root):
    with open(filepath, 'r') as f:
        log.debug('Parsing {}'.format(filepath))
        doc = yaml.load_all(f)
        data = {}
        try:
            for d in doc:
                log.debug(d)
                data = d
                break
        except Exception as e:
            log.error(e)
            log.error("Probably the file doesn't have YAML front matter.")

        title = data.get('title', 'Untitled')
        log.debug('Note title: {}'.format(title.encode('utf8')))
        tags = data.get('tags', ['Untagged'])
        log.debug('Note tags: {}'.format(tags))
        date = data.get('date', None)
        log.debug('Date: {}'.format(date))
        relpath = os.path.relpath(filepath, nb_root)
        note = Note(relpath, title, tags)
        note.set_date(date)
        return note


def get_nb_from_nb_dir(nb_dir):
    if not nb_dir:
        raise Exception('Not a Nota Bene directory!')

    nb_file_path = os.path.join(nb_dir, 'nb')
    log.debug('Database file path: {}'.format(nb_file_path))
    if os.path.isfile(nb_file_path):
        log.debug('Database file found.')
        nb = pickle.load(open(nb_file_path, 'rb'))
        return nb

    raise Exception('Database file not found. Nota Bene directory corrupted?')


def store(nb_dir, nb):
    pickle.dump(nb, open(os.path.join(nb_dir, 'nb'), "wb"))


def create_nb_dir(dir_path):
    log.debug('Initializing Nota Bene in {}'.format(dir_path))
    note_dir = os.path.join(dir_path, FOLDER_NAME)
    if os.path.exists(note_dir):
        log.error('{} directory already exists'.format(FOLDER_NAME))
        raise Exception('.not directory already exists')

    # TODO: Permission problems?
    log.debug('Creating {} directory'.format(FOLDER_NAME))
    os.makedirs(note_dir)
    return str(note_dir)
