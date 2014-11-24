#!/usr/bin/python
# -*- coding: utf-8 -*-
import SakaiPy.RequestGenerator



class UserSession(object):

	def __init__(self, rq):
        self.requester = rq