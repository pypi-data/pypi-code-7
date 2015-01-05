"""News to mail gateway script. Copyright 2000 Cosimo Alfarano

Author: Cosimo Alfarano
Date: June 11 2000

whitelist.py - (C) 2000 by Cosimo Alfarano <Alfarano@Students.CS.UniBo.It>
You can use this software under the terms of the GPL. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.

Thanks to md for this useful formula. Beer is beer.

whitelist manage a list of trusted user.
"""

import logging
# logging.basicConfig(level=logging.DEBUG)
import sys
import time

import wlp


class whitelist(object):
    """whitelist handling class

    Do you really want anyone can post? Ah ah ah.
    """
    wl = {}

    # constants
    DENY = 0
    ACCEPT = 1

    def __init__(self, wlfile, logfile='pyg.log'):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        log_fh = logging.FileHandler(logfile)
        log_fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_fh.setFormatter(log_fmt)
        self.logger.addHandler(log_fh)

        try:
            wlp.setfilebyname(wlfile)
        except Exception as ex:
            self.logger.exception('Opening %s: %s', wlfile, ex)
            sys.exit(1)

        # dict is a { ownername : {variable: value}} dictionary of dictionaries
        self.wl = wlp.mkdict()

    def checkfrom(self, fromhead):
        """have you permission to be here, sir?"""
        for owner in self.wl:
            # here colon after 'From' IS required, because binary module wl
            # expects it.
            # TODO: when switching to the python lexxing, remove this
            # limitation.
            if fromhead.find(self.wl[owner]['From:']) >= 0:
                return owner
            else:
                return None

    def logmsg(self, heads, ok=DENY, owner=None):
        """who are walking through my gate?
        """

        ltime = time.ctime(time.time())

        if time.daylight:
            tzone = time.tzname[1]
        else:
            tzone = time.tzname[0]

        if ok == self.ACCEPT:
            self.logger.info('Permission Accorded ')
        else:
            self.logger.info('Permission Denied ')

        self.logger.info('at %s (%s)', ltime, tzone)
        if owner is not None:
            self.logger.debug('\tWLOwner: ' + owner + '')
        self.logger.debug('\tFrom: ' + heads.get('From', 'NOT PRESENT'))
        self.logger.debug('\tSubject: ' + heads.get('Subject', 'NOT PRESENT'))
        self.logger.debug('\tSender: ' + heads.get('Sender', 'NOT PRESENT'))
        self.logger.debug('\tDate: ' + heads.get('Date', 'NOT PRESENT'))

        # some client create Message-Id other Message-ID.
        if 'Message-ID' in heads:
            self.logger.debug('\tMessage-ID: ' + heads.get('Message-ID'))
        else:
            self.logger.debug('\tMessage-Id: ' + heads.get('Message-Id',
                                                           'NOT PRESENT'))

        # X-Newsgroups: and To: are present if user is trusted, else
        # Newsgroup: exists since no changes on nntp headers are done.
        if 'X-Newsgroups' in heads:
            self.logger.debug('\tTo: ' + heads.get('To', 'NOT PRESENT'))
            self.logger.debug('\tX-Newsgroups: ' + heads.get('X-Newsgroups',
                                                             'NOT PRESENT'))
        else:
            self.logger.debug('\tNewsgroups: ' +
                              heads.get('Newsgroups', 'NOT PRESENT'))
