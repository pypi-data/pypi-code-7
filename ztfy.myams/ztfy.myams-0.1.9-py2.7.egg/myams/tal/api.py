#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.json.interfaces import IJSONWriter
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.myams.interfaces import IMyAMSApplication, IObjectData
from ztfy.myams.interfaces.configuration import IMyAMSConfiguration
from ztfy.myams.tal.interfaces import IMyAMSTalesAPI

# import Zope3 packages
from zope.component import getUtility
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.utils.traversing import getParent


class MyAMSTalesAdapter(object):
    """myams: TALES adapter"""

    implements(IMyAMSTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def data(self):
        data = IObjectData(self.context, None)
        if (data is not None) and data.object_data:
            writer = getUtility(IJSONWriter)
            return writer.write(data.object_data)

    def configuration(self):
        application = getParent(self.context, IMyAMSApplication)
        if application is not None:
            return IMyAMSConfiguration(application, None)

    def resources(self):
        application = getParent(self.context, IMyAMSApplication)
        if application is not None:
            for resource in application.resources:
                removeSecurityProxy(resource).need()
