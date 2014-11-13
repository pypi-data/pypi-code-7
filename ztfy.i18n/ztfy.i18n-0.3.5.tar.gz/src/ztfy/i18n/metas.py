### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.baseskin.interfaces.metas import IContentMetasHeaders

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements, Interface

# import local packages
from ztfy.baseskin.metas import HTTPEquivMeta, ContentMeta
from ztfy.i18n.interfaces.content import II18nBaseContent


class I18nBaseContentMetasHeadersAdapter(object):
    """Base content metas adapter"""

    adapts(II18nBaseContent, Interface)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        result = []
        result.append(HTTPEquivMeta('Content-Type', 'text/html; charset=UTF-8'))
        i18n = II18n(self.context, None)
        if i18n is None:
            return result
        description = i18n.queryAttribute('description', request=self.request)
        if description:
            result.append(ContentMeta('description', description.replace('\n', ' ')))
        keywords = i18n.queryAttribute('keywords', request=self.request)
        if keywords:
            result.append(ContentMeta('keywords', keywords))
        return result
