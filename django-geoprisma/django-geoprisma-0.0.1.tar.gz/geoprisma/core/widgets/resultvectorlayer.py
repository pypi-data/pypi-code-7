from geoprisma.utils import isAuthorized
from widgetbase import WidgetBase


class ResultVectorLayer(WidgetBase):

    def getServiceType(self):
        return "wms"

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("queryable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
