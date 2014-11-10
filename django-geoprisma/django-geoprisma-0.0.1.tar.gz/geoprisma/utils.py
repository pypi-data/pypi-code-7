# -*- coding: utf-8 -*-
from django.conf import settings
from .models import Resource
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import re


def join_url(*args):
    s = '/'.join(args)
    return re.sub(r'/+', '/', s)


def isAuthorized(user, ress_name, action_name):
    """
    Valid if a user has the right to do an action on a ressource.

    """
    #Import model that support PGSQL schema if difined
    if hasattr(settings,'ACL_UTILS'):
        try:
            utils = __import__(settings.ACL_UTILS, fromlist=['*'])
            return utils.isAuthorized(user, ress_name, action_name)
        except ImportError:
            raise Exception("ACL UTILS import Error")
    else:
        utils = __import__("geoprisma.acl.utils", fromlist=['*'])
        return utils.isAuthorized(user, ress_name, action_name)
