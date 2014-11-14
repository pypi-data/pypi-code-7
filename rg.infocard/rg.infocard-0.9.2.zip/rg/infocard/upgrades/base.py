# coding=utf-8
from .. import PRODUCT_ID
from plone import api

PROFILE_ID = 'profile-%s:default' % PRODUCT_ID


def upgrade_version(version):
    """ Upgrade version function """
    qi = api.portal.get_tool('portal_quickinstaller')
    p = qi.get(PRODUCT_ID)
    setattr(p, 'installedversion', version)


def upgrade_version_decorator(version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            upgrade_version(version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func
