# encoding: utf-8
"""
Created on 11/17/14

@author: Takashi NAGAI
"""

__author__ = 'nagai'

import time
import logging
from random import random
from datetime import datetime as dt
from dogapi import dog_http_api
import statsd
from plone import api
from AccessControl.SecurityInfo import ModuleSecurityInfo
try:
    from itertools import imap
except ImportError:
    imap = map
from ngi.notify.datadog import _

logger = logging.getLogger(__name__)
security = ModuleSecurityInfo('ngi.notify.datadog.dd')


class DogStasd4Plone(statsd.DogStatsd):
    """
    DogStatsd wrapper class
    """

    def _report(self, metric, metric_type, value, tags, sample_rate):
        if sample_rate != 1 and random() > sample_rate:
            return

        payload = [metric, u":", value, u"|", metric_type]
        if sample_rate != 1:
            payload.extend([u"|@", sample_rate])
        if tags:
            payload.extend([u"|#", u",".join(tags)])

        encoded = u"".join(imap(unicode, payload))
        self._send(encoded)


statsd_plone = DogStasd4Plone()


def _get_connect_string():
    """

    :return:
    """
    use_dogstatsd = statsd_host = statsd_port = dd_api_key = dd_app_key = host_name = ''
    try:
        use_dogstatsd = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.use_dogstatsd')
        statsd_host = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.statsd_host')
        statsd_port = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.statsd_port')
        dd_api_key = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.api_key')
        dd_app_key = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.application_key')
        host_name = api.portal.get_registry_record('ngi.notify.datadog.controlpanel.IDatadog.host_name')
    except:
        logging.warning('ngi.notify.datadog:No registry keys')
    return use_dogstatsd, statsd_host, statsd_port, dd_api_key, dd_app_key, host_name


def _dict2list(tags={}):
    return [u"{k}:{v}".format(k=k, v=v) for k, v in tags.items()]


security.declarePublic('metric_datadog')
def metric_datadog(metric_name, value=1.0, tags={}):
    """
    post to Datadog service
    :param metric_name:
    :param value:
    :param tags:
    :return:
    """

    use_dogstatsd, statsd_host, statsd_port, dd_api_key, dd_app_key, host_name = _get_connect_string()

    if metric_name:
        dd_tags = _dict2list(tags)
        if use_dogstatsd:
            statsd_plone.connect(statsd_host, statsd_port)
            statsd_plone.gauge(metric_name, value, tags=dd_tags)
        elif dd_api_key:
            dog_http_api.api_key = dd_api_key
            dog_http_api.application_key = dd_app_key
            dog_http_api.metric(metric_name, value, host=host_name, tags=dd_tags)


security.declarePublic('event_datadog')
def event_datadog(title, text, date_happened='', tags={}):
    """

    :param title:
    :param text:
    :param date_happened:
    :param tags:
    :return:
    """

    use_dogstatsd, statsd_host, statsd_port, dd_api_key, dd_app_key, host_name = _get_connect_string()

    if not date_happened:
        now = dt.now()
        date_happened = time.mktime(now.timetuple())

    if title and text:
        dd_tags = _dict2list(tags)
        if use_dogstatsd:
            statsd_plone.connect(statsd_host, statsd_port)
            statsd_plone.event(title, text, date_happened=date_happened, tags=dd_tags)
        elif dd_api_key:
            dog_http_api.api_key = dd_api_key
            dog_http_api.application_key = dd_app_key
            dog_http_api.event_with_response(title, text, date_happened=date_happened, tags=dd_tags, host=host_name)
