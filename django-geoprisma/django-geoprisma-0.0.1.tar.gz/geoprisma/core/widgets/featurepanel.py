from widgetbase import WidgetBase
from geoprisma.utils import isAuthorized
from geoprisma.models import WidgetType

class FeaturePanel_CustomForm(WidgetBase):

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)


class FeaturePanel_Selector(WidgetBase):

    def getServiceType(self):
        return "wms"

    def clone(self, resource):
        widgetClone = FeaturePanel_Selector()
        widgetClone.id = str(resource.id)+"_FPSClone"
        widgetClone.name = resource.name+"_FPSClone"
        widgetClone.type = WidgetType(name="featurepanel_selector")
        widgetClone.options  = {}
        widgetClone.options["fields"] = self.setFields(resource.fields)
        widgetClone.fields = resource.fields
        widgetClone.resource = resource
        widgetClone.addOrReplaceOption(resource)
        return widgetClone

    def hasClones(self):
        return True

    def linkResource(self, user, resourceList):
        self.widgetCloneList = []
        for resource in resourceList:
            if resource.getOption("result") == "featurepanelselector":
                if isAuthorized(user, resource.name, self.action):
                    self.widgetCloneList.append(self.clone(resource))

    def setFields(self, fields):
        fieldList = []
        for field in fields:
            fieldDic = {}
            fieldDic["name"] = field.name
            try:
                selectTypeOption = field.fieldoption_set.filter(name="selectType")[0]
                if selectTypeOption.value == "keyValue":
                    fieldDic["type"] = "key"
                    fieldList.append(fieldDic)
                    fieldDic["type"] = "value"
                    fieldList.append(fieldDic)
                elif selectTypeOption.value == "false":
                    pass
                else:
                    fieldDic["type"] = selectTypeOption.value
                    fieldList.append(fieldDic)
            except IndexError:
                pass
        return fieldList

    def getMandatoryResourceOptions(self):
        optionDic = {
            "result": "result",
            "primaryField": "fid",
            "selectorTemplate": "template",
            "selectorMethod": "method",
            "selectorTemplateHeight": "height",
            "selectorTemplateWidth": "width"
        }
        return optionDic

    def getClones(self):
        return self.widgetCloneList
