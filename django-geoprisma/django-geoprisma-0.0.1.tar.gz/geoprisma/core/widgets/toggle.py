from geoprisma.utils import isAuthorized
from widgetbase import WidgetBase

class Toggle(WidgetBase):

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("toggleResource"):
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
