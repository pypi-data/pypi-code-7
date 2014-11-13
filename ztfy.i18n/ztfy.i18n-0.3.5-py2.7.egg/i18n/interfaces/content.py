#
# Copyright (c) 2008-2014 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.base.interfaces import IBaseContent
from ztfy.i18n.interfaces import II18nAttributesAware
from ztfy.i18n.schema import I18nTextLine, I18nText, I18nImage, I18nCthumbImage

# import Zope3 packages

# import local packages

from ztfy.i18n import _


#
# I18n aware contents interfaces
#

class II18nBaseContent(IBaseContent, II18nAttributesAware):
    """Base content interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Content title"),
                         required=True)

    shortname = I18nTextLine(title=_("Short name"),
                             description=_("Short name of the content can be displayed by several templates"),
                             required=True)

    description = I18nText(title=_("Description"),
                           description=_("Internal description included in HTML 'meta' headers"),
                           required=False)

    keywords = I18nTextLine(title=_("Keywords"),
                            description=_("A list of keywords matching content, separated by commas"),
                            required=False)

    header = I18nImage(title=_("Header image"),
                       description=_("This banner can be displayed by skins on page headers"),
                       required=False)

    heading = I18nText(title=_("Heading"),
                       description=_("Short header description of the content"),
                       required=False)

    illustration = I18nCthumbImage(title=_("Illustration"),
                                   description=_("This illustration can be displayed by several presentation templates"),
                                   required=False)

    illustration_title = I18nTextLine(title=_("Illustration alternate title"),
                                      description=_("This text will be used as an alternate title for the illustration"),
                                      required=False)