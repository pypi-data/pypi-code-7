__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging

from zope.i18nmessageid import MessageFactory
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils
from Products.validation.exceptions import AlreadyRegisteredValidatorError

from plonehrm.contracts import config
from Products.validation import validation
from validators import MaxDaysPerWeek
validation.register(MaxDaysPerWeek('maxDaysPerWeek'))
logger = logging.getLogger('plonehrm.contracts')
logger.debug('Installing Product')
ContractsMessageFactory = MessageFactory(u'contract')

try:
    from plonehrm.contracts import validators
    validators  # pyflakes
except AlreadyRegisteredValidatorError:
    pass


def initialize(context):
    import content
    content  # pyflakes
    from content import tool
    tool  # pyflakes

    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types=content_types,
        permission='plonehrm: Add contract',
        extra_constructors=constructors,
        fti=ftis,
    ).initialize(context)
