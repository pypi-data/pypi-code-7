from geoprisma.utils import isAuthorized
from widgetbase import WidgetBase


class ResultExtGrid(WidgetBase):

    def getServiceType(self):
        return "wms"

    def linkResource(self, user, resourceList):
        self.resources = []
        if self.getOption("useResponseFields") == "true":
            return

        objGrids = None

        for resource in resourceList:
            if resource.getOption("result") == "resultextgrid":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
                    resource.addWidget(self)
