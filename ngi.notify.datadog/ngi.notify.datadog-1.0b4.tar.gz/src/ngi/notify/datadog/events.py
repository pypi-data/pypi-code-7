# encoding: utf-8
"""
Created on 07/18/14

@author: Takashi NAGAI
"""
import time
from datetime import datetime as dt
from plone import api
from ngi.notify.datadog import _
from ngi.notify.datadog import dd_msg_pool
from ngi.notify.datadog.dd import (metric_datadog,
                                   event_datadog)


def createdContent(obj, event):
    """
    Created Event
    """
    user = api.user.get_current()
    path = '/'.join(obj.getPhysicalPath())
    try:
        state = api.content.get_state(obj=obj)
    except:
        state = 'none'
    portal_type = obj.portal_type
    content_type = obj.Type()
    metric_name = 'plone.created'
    tags = dict(user=user.id,
                path=path,
                title=obj.title,
                content_type=content_type,
                portal_type=portal_type,
                workflow=state)
    metric_datadog(metric_name, tags=tags)


def modifiedContent(obj, event):
    """
    Modified Event
    """
    user = api.user.get_current()
    path = '/'.join(obj.getPhysicalPath())
    try:
        state = api.content.get_state(obj=obj)
    except:
        state = 'none'
    portal_type = obj.portal_type
    content_type = obj.Type()
    metric_name = 'plone.modified'
    tags = dict(user=user.id,
                path=path,
                title=obj.title,
                content_type=content_type,
                portal_type=portal_type,
                workflow=state)
    metric_datadog(metric_name, tags=tags)


def actionSucceeded(obj, event):
    """

    :param obj:
    :param event:
    :return:
    """
    #import pdb;pdb.set_trace()
    user = api.user.get_current()
    path = '/'.join(obj.getPhysicalPath())
    try:
        state = api.content.get_state(obj=obj)
    except:
        state = 'none'
    portal_type = obj.portal_type
    content_type = obj.Type()
    wf_action = event.action
    metric_name = 'plone.workflow_action'
    tags = dict(user=user.id,
                path=path,
                title=obj.title,
                content_type=content_type,
                portal_type=portal_type,
                action=wf_action,
                workflow=state)
    metric_datadog(metric_name, tags=tags)


def _log_in_out(metric_name, obj):
    """

    :param metric_name:
    :param obj:
    :return:
    """
    user = api.user.get_current()
    path = '/'.join(obj.getPhysicalPath())
    metric_name = metric_name
    tags = dict(user=user.id,
                path=path)
    metric_datadog(metric_name, tags=tags)


def loggedIn(obj, event):
    """
    logged_out event
    :param obj:
    :param event:
    :return:
    """
    _log_in_out('plone.login', obj)


def loggedOut(obj, event):
    """
    logged_out event
    :param obj:
    :param event:
    :return:
    """
    _log_in_out('plone.logout', obj)


def userCreated(event):
    """

    :param event:
    :return:
    """
    principal = event.principal
    new_userid = principal.getUserId()
    user = api.user.get_current()
    metric_name = 'plone.created_user'
    tags = dict(user=user.id,
                userid=new_userid)
    metric_datadog(metric_name, tags=tags)


def userDeleted(event):
    """

    :param event:
    :return:
    """
    principal = event.principal
    delete_userid = principal
    user = api.user.get_current()
    metric_name = 'plone.deleted_user'
    tags = dict(user=user.id,
                userid=delete_userid)
    metric_datadog(metric_name, tags=tags)


def cpChanged(event):
    """

    :param event:
    :return:
    """
    #import pdb;pdb.set_trace()

    user = api.user.get_current()
    metric_name = 'plone.configuration_changed'
    path = event.context.request.getURL()
    tags = dict(user=user.id,
                path=path)
    metric_datadog(metric_name, tags=tags)


def actionRaisedEvent(obj, event):
    """

    :param obj:
    :param event:
    :return:
    """
    title = _(u'Workflow action error')
    text = _(u'Workflow action error')
    tags = dict()
    event_datadog(
        title,
        text,
        tags=tags
    )


def _start_process(title, text, tags):
    global dd_msg_pool
    now = dt.now()
    date_happened = time.mktime(now.timetuple())
    msg = dict(type=u'dd_event',
               title=title,
               text=text,
               date_happened=date_happened,
               tags=tags)
    dd_msg_pool.append(msg)


def processStart(event):
    """

    :param event:
    :return:
    """
    #import pdb;pdb.set_trace()
    title = _(u"Zope Process Start")
    text = _(u"Zope Process Start")
    tags = {}
    _start_process(title, text, tags)


def databaseOpened(event):
    """

    :param event:
    :return:
    """

    title = _(u"ZODB Opened")
    text = _(u"ZODB Opened")
    tags = {}
    _start_process(title, text, tags)