#
# Copyright (c) 2014 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from zope.session.interfaces import ISessionDataContainer

# import local interfaces

# import Zope3 packages
from zope.schema import Choice

# import local packages

from ztfy.beaker import _


class IBeakerSessionUtility(ISessionDataContainer):
    """Beaker session utility"""

    configuration_name = Choice(title=_("Beaker session configuration name"),
                                description=_("Name of Beaker configuration utility"),
                                vocabulary="ZTFY Beaker sessions configurations",
                                required=False,
                                default=u'')
