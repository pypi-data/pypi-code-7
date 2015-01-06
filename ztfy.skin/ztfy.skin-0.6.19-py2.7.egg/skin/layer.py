### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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
from jquery.layer import IJQueryJavaScriptBrowserLayer

# import local interfaces
from ztfy.baseskin.layer import IBaseSkinLayer

# import Zope3 packages

# import local packages


class IBaseZTFYLayer(IBaseSkinLayer):
    """ZTFY base layer"""


class IZTFYBrowserLayer(IBaseZTFYLayer, IJQueryJavaScriptBrowserLayer):
    """ZTFY JavaScript layer"""


class IZTFYBackLayer(IZTFYBrowserLayer):
    """ZTFY back-office layer"""


class IZTFYFrontLayer(IZTFYBrowserLayer):
    """ZTFY front-office layer"""
