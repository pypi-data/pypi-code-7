# -*- coding: utf-8 -*-
"""
Created on 2014/11/18

@author: nagai
"""

__author__ = 'nagai'

from plone import api
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from ngi.notify.datadog import _
from ngi.notify.datadog import dd_msg_pool
from ngi.notify.datadog.dd import (metric_datadog,
                                   event_datadog)


class CronDatadog(BrowserView):

    def __call__(self):

        context = self.context
        request = context.REQUEST

        #pool data
        global dd_msg_pool
        if dd_msg_pool:
            for x in dd_msg_pool:
                if x['type'] == 'dd_event':
                    event_datadog(
                        x['title'],
                        x['text'],
                        date_happened=x['date_happened'],
                        tags=x['tags']
                    )
                elif x['type'] == 'dd_metric':
                    metric_datadog(
                        x['metric_name'],
                        x['value'],
                        tags=x['tags']
                    )
            dd_msg_pool = []

        #DB size
        metric_name = 'plone.db_info'
        db_name, value = self.db_info()
        db_tags = dict(db_name=db_name)
        metric_datadog(metric_name, value=value, tags=db_tags)

        return True

    def db_info(self):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        return cpanel.db_name(), float(cpanel.db_size()[0:-1])