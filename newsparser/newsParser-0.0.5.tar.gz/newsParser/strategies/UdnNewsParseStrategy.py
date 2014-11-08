#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Balicanta.Yao
# @Date:   2014-10-25 01:02:36
# @Last Modified by:   balicanta
# @Last Modified time: 2014-10-25 10:47:27

from AbstractNewsParseStrategy import AbstractNewsParseStrategy


class UdnNewsParseStrategy(AbstractNewsParseStrategy):

    def isURLMatch(self, url):
        return "udn.com" in url

    def getTitle(self, beautiful_soup_object):
        return beautiful_soup_object.select('#story_title')[0].text

    def getAuthor(self, beautiful_soup_object):
        return beautiful_soup_object.select('#story_author')[0].text

    def getContent(self, beautiful_soup_object):
        return beautiful_soup_object.select('#story')[0].text

    def getPublishDate(self, beautiful_soup_object):
        return beautiful_soup_object.select('#story_update')[0].text
