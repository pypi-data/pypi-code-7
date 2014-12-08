#!/usr/bin/env python
# -*- coding:utf-8 -*-

from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import NoteSortOrder
import evernote.edam.notestore.ttypes as NoteStore
from clint import textui
import sys
import os
import re
import argparse
import ConfigParser
import keyring
import config as sys_config
import pickle
from xml.dom import minidom, Node as XmlNode


class Snipe():
    def __init__(self, token, sandbox=True):
        self.client = EvernoteClient(token=token, sandbox=sandbox)
        self.client_note_store = self.client.get_note_store()
        self.tag = sys_config.note_default_tag
        self.limit = sys_config.note_max_limit
        self.bookguid = None

    def setMetaNotes(self):
        filter = NoteStore.NoteFilter()
        filter.order = NoteSortOrder.TITLE
        filter.tagGuids = [self.getTagGuid(self.tag)]
        filter.ascending = True
        spec = NoteStore.NotesMetadataResultSpec()
        spec.includeTitle = True
        notes_metadata = self.client_note_store.findNotesMetadata(filter, 0, self.limit, spec)
        meta_notes = [x for x in notes_metadata.notes]
        meta_notes = dict(zip(range(1, len(meta_notes)+1), meta_notes))
        Snipe.saveNotes(sys_config.filepath_dump, meta_notes)
        return meta_notes

    def getNoteContent(self, number):
        meta_notes = Snipe.getNotes(sys_config.filepath_dump)
        number = int(number)
        note = self.client_note_store.getNote(meta_notes[number].guid, True, True, True, True)
        return note.content.decode("utf-8")

    def getTagGuid(self, name):
        for v in self.client.get_note_store().listTags():
            if v.name == name:
                return v.guid
        return False

    @staticmethod
    def saveNotes(filepath, notes):
        f = open(filepath, 'w')
        pickle.dump(notes, f)
        f.close()

    @staticmethod
    def getNotes(filepath):
        f = open(filepath, 'r')
        notes = pickle.load(f)
        f.close()
        return notes

    @staticmethod
    def enexParse(node):
        n = node.firstChild
        while n:
            if n.nodeType is XmlNode.ELEMENT_NODE:
                Snipe.enexParse(n)
            elif n.nodeType is XmlNode.TEXT_NODE and len(n.nodeValue.rstrip('\n')) is not 0:
                print n.nodeValue.replace('!br!', '').encode('utf_8')
            n = n.nextSibling


class UserConfig():
    def __init__(self, filepath):
        self.filepath = filepath
        self.user_config = ConfigParser.SafeConfigParser()
        try:
            if not os.path.isfile(self.filepath):
                raise IOError(self.filepath)
        except:
            user_config = ConfigParser.RawConfigParser()
            user_config.add_section(sys_config.application_name)
            user_config.set(sys_config.application_name, 'tag', '')
            with open(self.filepath, 'wb') as configfile:
                user_config.write(configfile)
                os.chmod(self.filepath, 0644)
        self.user_config.read(self.filepath)

    def getUserOption(self, option):
        if self.user_config.has_option(sys_config.application_name, option):
            return self.user_config.get(sys_config.application_name, option)

    def setDeveloperToken(self):
        print(textui.colored.green('Get Evernote DeveloperToken URL --> ' + sys_config.token_geturl))
        while True:
            developer_token = raw_input('DeveloperToken: ')
            if self.isDeveloperToken(developer_token, sys_config.sandbox):
                keyring.set_password(sys_config.application_name, 'developer_token', developer_token)
                return self

    def setDefaultTag(self):
        print(textui.colored.green("Set search tag / Default is 'Snipe'"))
        tag = raw_input('Search tag: ')
        self.user_config.set(sys_config.application_name, 'tag', tag)
        return self

    def save(self):
        self.user_config.write(open(self.filepath, 'w'))

    @staticmethod
    def isDeveloperToken(token, sandbox=True):
        try:
            EvernoteClient(token=token, sandbox=sandbox).get_note_store()
        except:
            print(textui.colored.red('Token can not be used'))
            return False
        return True


def main():
    parser = argparse.ArgumentParser(description=sys_config.application_name + ' version ' + sys_config.version)
    parser.add_argument('number', nargs='?', action='store', help='number of snippet')
    parser.add_argument('--config', action='store_true', help='set user config')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + sys_config.version)

    args = parser.parse_args()
    user_config = UserConfig(sys_config.filepath_user)

    if args.config:
        try:
            user_config.setDeveloperToken().setDefaultTag().save()
        except:
            return 1
        return 0

    stdin_dafault = sys.stdin
    sys.stdin = open('/dev/tty', 'rt')
    if not user_config.isDeveloperToken(keyring.get_password(sys_config.application_name, 'developer_token'), sys_config.sandbox):
        user_config.setDeveloperToken()
    sys.stdin = stdin_dafault

    snipe = Snipe(keyring.get_password(sys_config.application_name, 'developer_token'), sys_config.sandbox)

    tag = user_config.getUserOption('tag')
    if len(tag) > 0:
        snipe.tag = tag

    if args.number is not None:
        try:
            enex = snipe.getNoteContent(args.number)
        except:
            return 1
        enex = re.sub(r"<br>|<br/>", '!br!', enex)
        dom = minidom.parseString(enex.encode('utf_8'))
        Snipe.enexParse(dom)
        return 0

    print textui.colored.green("Search tag --> '" + snipe.tag + "'")

    try:
        for k, v in snipe.setMetaNotes().items():
            print textui.colored.blue("No " + str(k) + " : " + v.title)
        return 0
    except:
        return 1

if __name__ == "__main__":
    sys.exit(main())
