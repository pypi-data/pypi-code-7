# -*- coding: utf-8 -*-
"""
====================================================================
Functions for string manipulation (:mod:`pksci.tools._strfuncs`)
====================================================================

.. currentmodule:: pksci.tools._strfuncs

"""
from __future__ import absolute_import, division, print_function

import re

__all__ = ['concat_units', 'plural_word_check', 'split_replace']


def concat_units(var, units, rawstr=False, ucstr=False):
    """Concatenate variable with units in parentheses.

    Parameters
    ----------
    var, units : str
    rawstr, ucstr : bool, optional

    Returns
    -------
    str

    """
    if rawstr:
        return r'{} ({})'.format(var, units)
    elif ucstr:
        return u'{} ({})'.format(var, units)
    else:
        return '{} ({})'.format(var, units)


def plural_word_check(word, count):
    """Make a word plural by adding an *s* if ``count`` != 1.

    Parameters
    ----------
    word : str
        the word
    count : int
        the word count

    Returns
    -------
    str

    """
    return word if count == 1 else word + 's'


def split_replace(s, re_char='\W', replace=' ', replace_with='_'):
    """Split a string with regex and replace characters.

    Parameters
    ----------
    s : str
        the input string
    re_char : str
        regex character to split string with
    replace : str
        string to replace
    replace_with : str
        replacement string

    Returns
    -------
    str

    """
    return ''.join(re.split(re_char, s.replace(replace, replace_with)))
