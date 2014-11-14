""" CMFPlone tool interfaces.

$Id: _tools.py 38762 2005-10-05 10:44:00Z yuppie $
"""

from zope.interface import Interface
from zope.interface import Attribute


class IPropertiesTool(Interface):

    """ Manage properties of the site as a whole.
    """

    id = Attribute('id', 'Must be set to "portal_properties"')

    def editProperties(props):
        """ Change portal settings.

        Permission --  Manage portal
        """

    def smtp_server():
        """ Get local SMTP server.

        Returns -- String
        """


class ISimpleItemWithProperties(Interface):
    pass
