# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.app.discussion.interfaces import IConversation
from plone import api
from blog.post.browser import utils


class BlogView(BrowserView):
    """Blog View class"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.effdate = self.context.effective_date

    def get_total_comments(self):
        try:
            conversation = IConversation(self.context)
            return conversation.total_comments
        except TypeError:
            return 0

    def get_datetime_human(self):
        if self.effdate:
            return api.portal.get_localized_time(datetime=self.effdate)
        else:
            return False

    def get_author_name(self):
        return utils.get_author_name(self.context)

    def get_author_url(self):
        return utils.get_author_url(self.context)
