#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Balicanta.Yao
# @Date:   2014-10-24 13:34:05
# @Last Modified by:   balicanta
# @Last Modified time: 2014-10-25 10:47:33

from abc import ABCMeta, abstractmethod


class AbstractNewsParseStrategy():

    __metaclass__ = ABCMeta

    # Check Url is matching this strategy
    @abstractmethod
    def isURLMatch(self, url):
        pass

    # Get News Title
    @abstractmethod
    def getTitle(self, beautiful_soup_object):
        pass

    # Get News Title
    @abstractmethod
    def getAuthor(self, beautiful_soup_object):
        pass

    # Get Publish Date
    def getPublishDate(self, beautiful_soup_object):
        pass
