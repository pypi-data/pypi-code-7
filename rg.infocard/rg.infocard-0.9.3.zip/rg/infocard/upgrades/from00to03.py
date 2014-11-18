# coding=utf-8
from .. import rg_infocard_logger as logger
from .base import PROFILE_ID
from .base import upgrade_version_decorator
from plone import api


@upgrade_version_decorator('3')
def upgrade(context):
    ''' Reread portlets.xml
    '''
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'portlets')
    logger.info("Portlets has been updated")
