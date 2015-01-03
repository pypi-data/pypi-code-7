"""IRC log file format definitions."""
# pylint: disable=invalid-name,line-too-long


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import re


def c(regex):
    """A convenience alias for anchoring and compiling *regex*."""
    return re.compile(r'^{}$'.format(regex))


#: A dict mapping supported formats to their rules.
formats = {
    'omnipresence': {
        'line':         c(r'\[(?P<timestamp>.*?)\]  (?P<line>.*)'),
        'timestamp':    '%d-%b-%Y %H:%M:%S',
        'privmsg':      c(r'<(?P<nick>.*?)> (?P<content>.*)'),
        'action':       c(r'\* (?P<nick>.*?) (?P<content>.*)'),
        'notice':       c(r'-(?P<nick>.*?)- (?P<content>.*)'),
        'nick':         c(r'\*\*\* (?P<oldnick>.*?) is now known as (?P<newnick>.*?)'),
        'join':         c(r'\*\*\* (?P<nick>.*?) <(?P<hostmask>.*?)> has joined (?P<channel>.*?)'),
        'part':         c(r'\*\*\* (?P<nick>.*?) <(?P<hostmask>.*?)> has left (?P<channel>.*?)'),
        'quit':         c(r'\*\*\* (?P<nick>.*?) <(?P<hostmask>.*?)> has quit IRC(?: \((?P<content>.*?)\))?'),
        'kick':         c(r'\*\*\* (?P<kickee>.*?) was kicked by (?P<kicker>.*?)(?: \((?P<content>.*?)\))?'),
        'topic':        c(r'\*\*\* (?P<nick>.*?) changes topic to (?P<content>.*?)'),
        'mode':         c(r'\*\*\* (?P<nick>.*?) sets mode: (?P<content>.*?)'),
    },
}
