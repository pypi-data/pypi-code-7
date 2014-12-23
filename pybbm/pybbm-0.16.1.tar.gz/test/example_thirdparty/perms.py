# coding=utf-8
from __future__ import unicode_literals
from pybb.permissions import DefaultPermissionHandler


class Perms(DefaultPermissionHandler):
    def may_create_poll(self, user):
        return True