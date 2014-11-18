# coding=utf-8
from .base import upgrade_version_decorator
from plone import api


@upgrade_version_decorator('2')
def upgrade(context):
    '''
    Migrate the contents after schema modifications
    '''
    pc = api.portal.get_tool('portal_catalog')
    brains = pc(
        portal_type=[
            "infocardcontainer",
            "infocard",
        ])
    for brain in brains:
        obj = brain.getObject()
        if hasattr(obj, 'locations'):
            obj.servicetypes = obj.locations
            delattr(obj, 'locations')
            obj.reindexObject()
