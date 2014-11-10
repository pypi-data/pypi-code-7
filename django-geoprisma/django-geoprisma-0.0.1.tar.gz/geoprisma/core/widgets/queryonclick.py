from geoprisma.utils import isAuthorized
from widgetbase import WidgetBase


class QueryOnClick(WidgetBase):

    def getServiceType(self):
        return "wms"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("queryable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
                    resource.addWidget(self)
        if len(self.resources) == 0:
            self.toAdd = False

