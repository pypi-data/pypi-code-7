#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: bustta
# @Date:   2014-10-27 22:59:12
# @Last Modified by:   bustta
# @Last Modified time: 2014-10-27 23:19:51
from AbstractNewsParseStrategy import AbstractNewsParseStrategy


class LtnNewsParseStrategy(AbstractNewsParseStrategy):

    def isURLMatch(self, url):
        # http://news.ltn.com.tw/news/business/breakingnews/1142153
        return ".ltn.com" in url

    def getTitle(self, beautiful_soup_object):
        title = beautiful_soup_object.find(
            "div", "content").h1.text
        return title

    def getAuthor(self, beautiful_soup_object):
        return "LtnNews"

    def getContent(self, beautiful_soup_object):
        paragraph_list = beautiful_soup_object.find(id="newstext").find_all(
            "p", recursive=False)
        content = ""
        for item in paragraph_list:
            content += item.text.strip()

        return content

    def getPublishDate(self, beautiful_soup_object):
        time = beautiful_soup_object.find(
            id="newstext").span.text
        return time
