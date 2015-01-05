"""Mail to news gateway script. Copyright 2000 Cosimo Alfarano

Author: Cosimo Alfarano
Date: September 16 2000

mail2news.py - (C) 2000 by Cosimo Alfarano <Alfarano@Students.CS.UniBo.It>
You can use this software under the terms of the GPL. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.

Thanks to md for this useful formula. Beer is beer.

Gets news email and sends it via SMTP.

class mail2news is  hopefully conform to rfc850.

"""
from StringIO import StringIO
from collections import OrderedDict
import email
import logging
import nntplib
import os
from re import findall
from socket import gethostbyaddr, gethostname
import sys


#logging.basicConfig(level=logging.DEBUG)
# This is the single source of Truth
# Yes, it is awkward to have it assymetrically here
# and not in news2mail as well.
VERSION = '0.9.14'
DESC = "The Python Gateway Script: news2mail mail2news gateway"


class mail2news(object):
    """news to mail gateway class"""

    def __init__(self, options):
        #    newsgroups = None  # Newsgroups: local.test,local.moderated...
        #    approved = None  # Approved: kame@aragorn.lorien.org
        if 'NNTPHOST' in os.environ:
            self.newsserver = os.environ['NNTPHOST']
        else:
            self.newsserver = 'localhost'

        self.port = 119
        self.user = None
        self.password = None
        self.verbose = options.verbose
        logging.debug('self.verbose = %s', self.verbose)

        self.hostname = gethostbyaddr(gethostname())[0]

        self.heads_dict, self.smtpheads, self.nntpheads = {}, {}, {}
        self.message = self.__readfile(options)

        self.message['X-Gateway'] = 'pyg {0} {1}'.format(VERSION, DESC)

    def __add_header(self, header, value, msg=None):
        if msg is None:
            msg = self.message
        if value:
            msg[header] = value.strip()

    def __readfile(self, opt):
        message = email.message_from_file(sys.stdin)

        if (len(message) == 0) \
                and message.get_payload().startswith('/'):
            msg_file_name = message.get_payload().strip()
            del message
            with open(msg_file_name, 'r') as msg_file:
                message = email.message_from_file(msg_file)

        # introduce nntpheads
        self.__add_header('Newsgroups', opt.newsgroup, message)
        self.__add_header('Approved', opt.approver, message)

        return message

    def renameheads(self):
        """rename headers such as Resent-*: to X-Resent-*:

        headers renamed are useless or not rfc 977/850 copliant
        handles References/In-Reply-To headers
        """
        try:

            for key in self.message.keys():
                if key.startswith('Resent-'):
                    if ('X-' + key) in self.message:
                        self.message['X-Original-' + key] = \
                            self.message['X-' + key]
                    self.message['X-' + key] = self.message[key]
                    del self.message[key]

            # In rfc822 References: is considered, but many MUA doen't put it.
            if ('References' not in self.message) and \
                    ('In-Reply-To' in self.message):
                print self.message['In-Reply-To']

                # some MUA uses msgid without '<' '>'
#                ref = findall('([^\s<>\']+@[^\s<>;:\']+)', \
                # but I prefer use RFC standards
                ref = findall('(<[^<>]+@[^<>]+>)',
                              self.message['In-Reply-To'])

                # if found, keep first element that seems a Msg-ID.
                if(ref and len(ref)):
                    self.message['References'] = '%s\n' % ref[0]

        except KeyError, message:
            print message

    def removeheads(self, heads=None):
        """remove headers like Xref: Path: Lines:
        """

        try:
            # removing some others useless headers .... (From is not From:)

            rmheads = ['Received', 'From ', 'NNTP-Posting-Host',
                       'X-Trace', 'X-Compliants-To', 'NNTP-Posting-Date']
            if heads:
                rmheads.append(heads)

            for head in rmheads:
                if head in self.message:
                    del self.message[head]

            if 'Message-Id' in self.message:
                msgid = self.message['Message-Id']
                del self.message['Message-Id']
                self.message['Message-Id'] = msgid
            else:
                msgid = '<pyg.%d@tuchailepuppapera.org>\n' % (os.getpid())
                self.message['Message-Id'] = msgid

        except KeyError, message:
            print message

    def sortheads(self):
        """make list sorted by heads: From: To: Subject: first,
           others, X-*, X-Resent-* last"""

        heads_dict = OrderedDict(self.message)
        for hdr in self.message.keys():
            del self.message[hdr]

        # put at top
        head_set = ('Newsgroups', 'From', 'To', 'X-To', 'Cc', 'Subject',
                    'Date', 'Approved', 'References', 'Message-Id')

        logging.debug('heads_dict = %s', heads_dict)
        for k in head_set:
            if k in heads_dict:
                self.__add_header(k, heads_dict[k])

        for k in heads_dict:
            if not k.startswith('X-') and not k.startswith('X-Resent-') \
                    and k not in head_set:
                self.__add_header(k, heads_dict[k])

        for k in heads_dict:
            if k.startswith('X-'):
                self.__add_header(k, heads_dict[k])

        for k in heads_dict:
            if k.startswith('X-Resent-'):
                self.__add_header(k, heads_dict[k])

    def sendemail(self):
        "Talk to NNTP server and try to send email."
        # readermode must be True, otherwise we don't have POST command.
        server = nntplib.NNTP(self.newsserver, self.port, self.user,
                              self.password, readermode=True)

        logging.debug('self.verbose = %s', self.verbose)
        if self.verbose:
            server.set_debuglevel(2)

        server.post(StringIO(self.message.as_string()))

        server.quit()
