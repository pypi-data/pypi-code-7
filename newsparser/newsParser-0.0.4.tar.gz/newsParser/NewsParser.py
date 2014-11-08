#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: balicanta
# @Date:   2014-10-25 00:09:39
# @Last Modified by:   kenny.tsai
# @Last Modified time: 2014-11-04 18:00:33

import sys

from strategies.UdnNewsParseStrategy import UdnNewsParseStrategy
from strategies.WorldYamParseStrategy import WorldYamParseStrategy
from strategies.LtnNewsParseStrategy import LtnNewsParseStrategy
from strategies.AnntwNewsParseStrategy import AnntwNewsParseStrategy
from strategies.CoolLoudParseStrategy import CoolLoudParseStrategy
from strategies.PeopleNewsParseStrategy import PeopleNewsParseStrategy
from strategies.AbstractNewsParseStrategy import AbstractNewsParseStrategy

from requests.utils import get_encodings_from_content
from bs4 import BeautifulSoup
import requests


class NewsParser():
    url = None
    encode = None
    content_soup_object = None
    parse_strategy = None

    def __init__(self, URL):
        from strategies.AbstractNewsParseStrategy import AbstractNewsParseStrategy
        self.url = URL
        for parse_strategy in vars()['AbstractNewsParseStrategy'].__subclasses__():
            if parse_strategy().isURLMatch(URL):
                self.parse_strategy = parse_strategy()

    def _fetchContent(self):
        r = requests.get(self.url)
        # Dynamic Get Encode From Content, get First as default
        self.encoding = get_encodings_from_content(r.content)[0]

        # Set System default Codeing
        reload(sys)
        sys.setdefaultencoding(self.encoding)

        content = r.content.decode(self.encoding)
        return content

    def _validataion(self):
        if(self.content_soup_object is None):
            content = self._fetchContent()
            self.content_soup_object = BeautifulSoup(content)

        if(self.parse_strategy is None):
            print "Non Support URL", self.url

    def getTitle(self):
        self._validataion()
        title = self.parse_strategy.getTitle(self.content_soup_object)
        return title

    def getContent(self):
        self._validataion()
        content = self.parse_strategy.getContent(self.content_soup_object)
        return content

    def getAuthor(self):
        self._validataion()
        author = self.parse_strategy.getAuthor(self.content_soup_object)
        return author

    def getPublishDate(self):
        self._validataion()
        author = self.parse_strategy.getPublishDate(
            self.content_soup_object)
        return author
