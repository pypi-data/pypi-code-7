#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: kenny.tsai
# @Date:   2014-11-04 16:54:46
# @Last Modified by:   kenny.tsai
# @Last Modified time: 2014-11-04 18:01:51

from AbstractNewsParseStrategy import AbstractNewsParseStrategy


class PeopleNewsParseStrategy(AbstractNewsParseStrategy):

    def isURLMatch(self, url):
        # http://www.peoplenews.tw/news/80a3de53-1c06-4d30-a330-b76e335132f7
        return ".peoplenews.tw" in url

    def getTitle(self, beautiful_soup_object):
        return beautiful_soup_object.select('.news_title')[0].text

    def getAuthor(self, beautiful_soup_object):
        return beautiful_soup_object.select('.author')[0].text

    def getContent(self, beautiful_soup_object):
        return beautiful_soup_object.find(id='newscontent').text

    def getPublishDate(self, beautiful_soup_object):
        return beautiful_soup_object.select('.date')[0].text
