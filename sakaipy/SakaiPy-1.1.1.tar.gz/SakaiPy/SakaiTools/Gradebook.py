#!/usr/bin/python
# -*- coding: utf-8 -*-
import SakaiPy.RequestGenerator



class Gradebook(object):

	def __init__(self, rq):
        self.requester = rq



    def getAllMyGrades(self):
        return self.requester.executeRequest('/direct/calendar/my.json')