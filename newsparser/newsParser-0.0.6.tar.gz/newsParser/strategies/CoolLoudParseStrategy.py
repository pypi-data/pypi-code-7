#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: DinoLai
# @Date:   2014-11-02 12:15:36
# @Last Modified by:   DinoLai
# @Last Modified time: 2014-11-02 13:01:37

from AbstractNewsParseStrategy import AbstractNewsParseStrategy


class CoolLoudParseStrategy(AbstractNewsParseStrategy):

    def isURLMatch(self, url):
        return ".coolloud.org.tw" in url

    def getTitle(self, beautiful_soup_object):
        return beautiful_soup_object.select('.post-title')[0].text

    def getAuthor(self, beautiful_soup_object):
        return beautiful_soup_object.select('.post-content > p > font')[0].text

    def getContent(self, beautiful_soup_object):
        return beautiful_soup_object.select('.post-content')[0].text

    def getPublishDate(self, beautiful_soup_object):
        return beautiful_soup_object.select('.date-display-single')[0].text
