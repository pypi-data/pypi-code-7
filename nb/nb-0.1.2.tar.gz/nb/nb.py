import os
import logging
import datetime

import utils

log = logging.getLogger(__name__)

class Tag(object):
    def __init__(self, name):
        self.name = name
        self.notes = {}

    def add_note(self, note):
        self.notes[note.filepath] = note

    def remove_note(self, filepath):
        try:
            del self.notes[filepath]
        except:
            pass

    def get_note_set(self):
        note_set = set([])
        for n in self.notes.values():
            note_set.add(n)

        return note_set

    def __str__(self):
        return self.name

class NotaBene(object):
    def __init__(self):
        self.tags = {}

    def add_note(self, fpath, nb_dir):
        n = utils.get_note_from_file(fpath, nb_dir)
        log.debug('Note tags: {}'.format(n.tags))
        for t in n.tags:
            log.debug('Adding tag {} for file {}'.format(t.encode('utf8'), fpath))
            tag = self.tags.get(t, Tag(t))
            tag.add_note(n)
            self.tags[t] = tag
        log.debug('File added: {}'.format(fpath))

    def rm_note(self, filepath, nb_root):
        relpath = os.path.relpath(filepath, nb_root)
        for t in self.tags.values():
            t.remove_note(relpath)

    def file_list(self):
        log.debug('Listing all notes')
        note_list = set([])
        return self.tag_union(self.tags.keys())

    def tag_union(self, tags):
        log.debug('Listing notes for tags: {}'.format(', '.join(t for t in tags).encode('utf8')))
        note_set = set([])
        for t in tags:
            if t not in self.tags.keys():
                raise Exception('Unknown tag: {}'.format(t.encode('utf8')))
            note_set = note_set.union(self.tags[t].get_note_set())

        return note_set

    def tag_intersection(self, tags):
        log.debug('Listing notes for the intersection of tags: {}'.format(', '.join(t for t in tags).encode('utf8')))
        if len(tags) < 2:
            raise Exception('Intersection is not valid on single tag')

        note_set = None
        for t in tags:
            if t not in self.tags.keys():
                raise Exception('Unknown tag: {}'.format(t.encode('utf8')))
            if not note_set:
                note_set = self.tags[t].get_note_set()
            else:
                note_set = note_set.intersection(self.tags[t])

        return note_set

