
from plone.app.users.browser.personalpreferences import IPersonalPreferences
from zope.interface import Interface
from zope import schema

class IEnhancedUserDataSchema(IPersonalPreferences):
    """ Use all the fields from the default user data schema, and add the
    'buttonsDisabled' field
    """
    buttonsDisabled = schema.Bool(title=u'Disable transition button widget.', 
                                default=False,
                                description=u'Check to remove the transition button box from ALL pages.',
                                required=False
                                )
