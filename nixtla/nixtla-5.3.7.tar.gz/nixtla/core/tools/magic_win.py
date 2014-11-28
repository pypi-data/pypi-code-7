# -*- coding: utf-8 -*-
'''
Created on Nov 25, 2014

Dumb replacement for libmagic in windows systems

@author: curiel
'''

import mimetypes


def from_file(filepath, mime=True):
    mimetypes.init()
    guessed_type = mimetypes.guess_type(filepath)[0]
    return guessed_type