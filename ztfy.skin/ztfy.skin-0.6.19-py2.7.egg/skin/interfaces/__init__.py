### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import ITextWidget, ITextAreaWidget

# import local interfaces
from z3c.form import button
from z3c.formjs import jsaction
# most interfaces have moved to ZTFY.baseskin package; please use them directly...
# following imports are kept only for compatibility reasons
from ztfy.baseskin.interfaces import *
from ztfy.baseskin.interfaces.form import *

# import Zope3 packages
from zope.interface import Attribute, Interface
from zope.schema import Bool, TextLine

# import local packages

from ztfy.skin import _


#
# Default forms buttons interfaces
#

class IAddFormButtons(Interface):
    """Default add form buttons"""

    add = button.Button(name='add', title=_("Add"), condition=checkSubmitButton)


class IDialogAddFormButtons(Interface):
    """Default dialog add form buttons"""

    add = jsaction.JSButton(name='add', title=_("Add"))
    cancel = jsaction.JSButton(name='cancel', title=_("Cancel"))


class IDialogDisplayFormButtons(Interface):
    """Default dialog display form buttons"""

    dialog_close = jsaction.JSButton(name='close', title=_("Close"))


class IEditFormButtons(Interface):
    """Default edit form buttons"""

    submit = button.Button(name='submit', title=_("Submit"), condition=checkSubmitButton)
    reset = button.Button(name='reset', title=_("Reset"))


class IDialogEditFormButtons(Interface):
    """Default dialog edit form buttons"""

    dialog_submit = jsaction.JSButton(name='dialog_submit', title=_("Submit"), condition=checkSubmitButton)
    dialog_cancel = jsaction.JSButton(name='dialog_cancel', title=_("Cancel"))


#
# Custom widgets interfaces
#

class IDateWidget(ITextWidget):
    """Marker interface for date widget"""


class IDatetimeWidget(ITextWidget):
    """Marker interface for datetime widget"""


class IFixedWidthTextAreaWidget(ITextAreaWidget):
    """Marker interface for fixed width text area widget"""


#
# Default views interfaces
#

class IPropertiesMenuTarget(Interface):
    """Marker interface for properties menus"""


class IDialogMenu(Interface):
    """Dialog access menu interface"""

    target = Attribute(_("Target dialog class"))


#
# Breadcrumb interfaces
#

class IBreadcrumbInfo(Interface):
    """Get custom breadcrumb info of a given context"""

    visible = Bool(title=_("Visible ?"),
                   required=True,
                   default=True)

    title = TextLine(title=_("Title"),
                     required=True)

    path = TextLine(title=_("Path"),
                    required=False)


#
# Back-office custom properties marker interface
#

class ICustomBackOfficeInfoTarget(Interface):
    """Marker interface for custom back-office properties"""

    back_interface = Attribute(_("Back-office properties custom interface"))
