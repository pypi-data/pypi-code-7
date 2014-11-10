from widgetbase import WidgetBase
from geoprisma.utils import isAuthorized
from geoprisma.models import WidgetType


class EditFeature_Confirm(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
                    resource.addWidget(self)

class EditFeature_Copy(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    editTypeList = resource.getOption("editTypes")
                    editTypeOption = resource.getOption("editType")
                    if editTypeList:
                        for editType in editTypeList:
                            if editType == "copy":
                                self.resources.append(resource)
                                resource.addWidget(self)
                    elif editTypeOption == "copy" or not editTypeOption:
                        self.resources.append(resource)
                        resource.addWidget(self)

class EditFeature_Create(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def clone(self, resource):
        widgetClone = EditFeature_Create()
        widgetClone.id = str(self.id) + "_EFCClone"
        widgetClone.name = self.name + "_EFCClone"
        widgetClone.type = WidgetType(name="editfeature_create")
        widgetClone.options = {}
        widgetClone.fields = resource.fields
        widgetClone.resource = resource
        widgetClone.addOrReplaceOption(resource)
        resource.addWidget(widgetClone)
        return widgetClone

    def hasClones(self):
        return True

    def linkResource(self, user, resourceList):
        self.widgetCloneList = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user,resource.name, self.action):
                    editTypeList = resource.getOption("editTypes")
                    editTypeOption = resource.getOption("editType")
                    if editTypeList:
                        for editType in editTypeList:
                            if editType == "create":
                                self.widgetCloneList.append(self.clone(resource))
                    elif editTypeOption == "create" or not editTypeOption:
                        self.widgetCloneList.append(self.clone(resource))

    def getMandatoryResourceOptions(self):
        optionDic = {
            "editable": "editable",
            "geometryTypeString": "geometrytype"
            }
        return optionDic

    def getClones(self):
        return self.widgetCloneList


class EditFeature_Drag(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                editTypeList = resource.getOption("editTypes")
                editTypeOption = resource.getOption("editType")
                if isAuthorized(user, resource.name, self.action):
                    if editTypeList:
                        for editType in editTypeList:
                            if editType == "drag":
                                self.resources.append(resource)
                                resource.addWidget(self)
                    elif editTypeOption == "drag" or not editTypeOption:
                        self.resources.append(resource)
                        resource.addWidget(self)

class EditFeature_Update(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    editTypeList = resource.getOption("editTypes")
                    editTypeOption = resource.getOption("editType")
                    if editTypeList:
                        for editType in editTypeList:
                            if editType == "update":
                                self.resources.append(resource)
                                resource.addWidget(self)
                    elif editTypeOption == "update" or not editTypeOption:
                        self.resources.append(resource)
                        resource.addWidget(self)

    def getMandatoryResourceOptions(self):
        optionDic = {
            "editable": "editable",
            "geometryEditable": "editgeom"
            }
        return optionDic

class EditFeature_Split(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("splittable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    self.resources.append(resource)
                    resource.addWidget(self)

class EditFeature_Delete(WidgetBase):

    def getServiceType(self):
        return "featureserver"

    def needLayer(self):
        return True

    def linkResource(self, user, resourceList):
        self.resources = []
        for resource in resourceList:
            if resource.getOption("editable") == "true":
                if isAuthorized(user, resource.name, self.action):
                    editTypeList = resource.getOption("editTypes")
                    editTypeOption = resource.getOption("editType")
                    if editTypeList:
                        for editType in editTypeList:
                            if editType == "delete":
                                self.resources.append(resource)
                                resource.addWidget(self)
                    elif editTypeOption == "delete" or not editTypeOption:
                        self.resources.append(resource)
                        resource.addWidget(self)
