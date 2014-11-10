import json
import copy
from django.utils.safestring import mark_safe

class ResourceBase(object):

    def __init__(self, resourceModel):
        self.id = resourceModel.id
        self.acl_name = resourceModel.acl_name
        self.name = resourceModel.name
        self.slug = resourceModel.slug
        self.display_name = resourceModel.display_name
        self.options = self.setOptions(resourceModel.resourceoption_set.all())
        self.datastores = resourceModel.datastores
        self.fields = resourceModel.fields.all()
        self.widgets = []


    def setOptions(self, options):
        optionDic = {}
        for option in options:
            if optionDic.has_key(option.name):
                if isinstance(optionDic[option.name],list):
                    optionDic[option.name].append(self.castOption(option.value))
                else:
                    optionDic[option.name] = [optionDic[option.name],self.castOption(option.value)]
            else:
                optionDic[option.name] = self.castOption(option.value)
        # Ajout un "s" au option contenant une liste
        # pour eviter les problemes avec le javascript
        for key in optionDic.keys():
            if isinstance(optionDic[key],list):
                plurial_key = key+"s"
                optionDic[plurial_key] = optionDic.pop(key)
        return optionDic

    def castOption(self, option):
        """
        Fonction qui change le type de l'option selon ca valeur
        """
        if isinstance(option,str) or isinstance(option,unicode):
            if option.isdigit():
                return int(option)
            elif option == "true":
                return True
            elif option == "false":
                return False
            else:
                return option
        else:
            return option

    def getOption(self, optionName):
        try:
            if self.options[optionName] == True:
                return "true"
            elif self.options[optionName] == False:
                return "false"
            return self.options[optionName]
        except KeyError:
            return False

    def printOptions(self):
        return mark_safe(json.dumps(self.options))

    def getDatastoreByType(self, typeName):
        try:
            return self.datastores.filter(service__type__name__iexact=typeName)[0]
        except IndexError:
            return False

    def hasWidgetUsingServiceType(self, serviceType, checkNeedLayer=True):
        for widget in self.widgets:
            if widget.getServiceType().lower() == serviceType.lower() and (not checkNeedLayer or widget.needLayer()):
                return True
        else:
            return False

    def addWidget(self, widget):
        self.widgets.append(widget);
