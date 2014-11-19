#!/usr/bin/env python
# coding: utf-8
"""
Acoustic-Phonetic Index

This module provides a search-oriented interface to the [NLTK/TIMIT][] database.

[NLTK/TIMIT]: http://nltk.org/api/nltk.corpus.reader.html#timit-module
"""

# Python 2.7 Standard Library
import __builtin__

# Third-Party Librairies
import numpy as np
from nltk.corpus import timit

# Digital Audio Coding
from audio.bitstream import BitStream

#
# Metadata
# ------------------------------------------------------------------------------
#

from .about_index import *

#
# Index Search
# ------------------------------------------------------------------------------
#

def search(name=None, uid=None, type=None):
    """
    Return a list of items that match `name`, `uid`, and/or `type` attributes.
    """
    global _index

    if type is None:
       type = Item
    if _index is None:
        _index = _create_index()

    def match(item):
        return (uid is None or item.uid == uid) and isinstance(item, type)
    if name:
        items = _index.get(name) or []
    else:
        items = __builtin__.sum(_index.values(), [])
    items = [item for item in items if match(item)]
    items = sorted(items, key=lambda item: item.name)
    return IndexedList(items)


class Item(list):
    """
    Phonetic/Acoustic Item: an utterance (sentence), word or phone.

    An item has the following attributes:

      - `name:` sequence of letters that represents the item ; for phones,
        the TIMITBET symbols are used.

      - `uid:` the TIMIT identifier of the utterance it belongs to,
  
      - `span:` a pair `(start, end)` of its location within the utterance,

      - `audio:` the acoustic data as a one-dimensional numpy array of floats

      - `parent:` its parent in the utterance structure or `None`.

    Phonetic items are organized in hierarchical structures: an item may contain 
    other phonetic of lesser rank: utterances may contain words or phones and 
    words contain may contain phones. The hierachy is accessible with the `list`
    methods that the class inherits.
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        if "parent" not in kwargs:
            self.parent = None
        self[:] = args


class Phone(Item):
    def __str__(self):
        return self.name + " ({0}).".format(self.parent)
    __repr__ = __str__

class Word(Item):
    def __str__(self):
        return self.name + " [" + "-".join([phone.name for phone in self]) + "]"
    __repr__ = __str__

class Utterance(Item):
    def __str__(self):
        return self.name
    __repr__ = __str__

Sentence = Utterance

class IndexedList(list):
    def __str__(self):
        text = ""
        index_width = len(str(len(self) - 1))
        index = " {0:" + str(index_width) + "}. "
        for i, item in enumerate(self):
            text += " " + index.format(i) + str(item) + "\n"
        return text
    __repr__ = __str__


_index = None

def _create_index(uids=None):
    """
    Search the TIMIT database and create the phonetic dictionary and hierarchy.
    """
    index = {}
    def register(item):
        index.setdefault(item.name, []).append(item)

    if uids is None:
        uids = timit.utteranceids()   

    for uid in uids:
        raw = timit.audiodata(uid)
        bitstream = BitStream(raw)
        audio = bitstream.read(np.int16, len(bitstream) / 16).newbyteorder()
        audio = audio / float(2**15)
        name = " ".join(timit.words(uid))
        utterance = Utterance(name=name, uid=uid, span=(0, len(audio)), audio=audio)
        register(utterance)

        words = [] 
        for name, start, end in timit.word_times(uid):
            word = Word(name=name, uid=uid, 
                        span=(start, end), audio=audio[start:end], 
                        parent=utterance)
            words.append(word)
            register(word)

        phones = []
        for name, start, end in timit.phone_times(uid):
            # the proper phone parent (utterance or word) is unknown.
            phone = Phone(name=name, uid=uid, 
                         span=(start, end), audio=audio[start:end])
            phones.append(phone)

        items = words
        for phone in phones:
            for word in words:
                if word.span[0] <= phone.span[0] and phone.span[1] <= word.span[1]:
                    phone.parent = word
                    word.append(phone)
                    break
            else:
                phone.parent = utterance
                items.append(phone)
            register(phone)

        items = sorted(items, key=lambda item: item.span)
        utterance[:] = items
    return index

_index = None

