import copy
from widgetbase import WidgetBase
from geoprisma.utils import isAuthorized
from geoprisma.models import WidgetType

class MapFishRecenter(WidgetBase):

    def hasClones(self):
        return True

    def linkResource(self, user, resourceList):
        self.widgetCloneList = []
        for resource in resourceList:
            if isAuthorized(user, resource.name, self.action):
                if resource.getOption("zoomField") or resource.getOption("zoomFields"):
                    widgetClone = MapFishRecenter()
                    widgetClone.id = str(resource.id) + "_MFRClone"
                    widgetClone.name = resource.name + "_MFRClone"
                    widgetClone.type = WidgetType(name="mapfishrecenter")
                    widgetClone.options = copy.copy(self.options)
                    widgetClone.options["fields"] = self.setFields(resource.fields)
                    widgetClone.resource = resource
                    self.widgetCloneList.append(widgetClone)


    def setFields(self, fields):
        fieldList = []
        for field in fields:
            fieldDic = {}
            fieldDic["queryparam"] = field.name
            fieldDic["displayfield"] = field.name
            if field.title:
                fieldDic["label"] = field.title
            else:
                fieldDic["label"] = field.name
            try:
                filterOption = field.fieldoption_set.filter(name="filter")[0]
                fieldDic["filter"] - filterOption.value
            except IndexError:
                pass
            fieldList.append(fieldDic)
        return fieldList

    def getClones(self):
        return self.widgetCloneList
