import json
import re
from django.utils.safestring import mark_safe

class WidgetBase(object):
    """
    Classe de base pour les widgets
    """

    def __init__(self, widgetModel=None):
        if widgetModel:
            self.id = widgetModel.id
            self.name = widgetModel.name
            self.type = widgetModel.type
            self.action = widgetModel.type.action
            self.toAdd = True
            self.options = self.setOptions(widgetModel.widgetoption_set.all())

    def getServiceType(self):
        return ""

    def needLayer(self):
        return False

    def setOptions(self, options):
        """
        Definie les options d'un widget en les formatant

        Args:
            options: Liste d'option

        Returns:
            Tableau d'option
        """
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
        Change le type de l'option selon ca valeur

        Args:
            option: L'option a caster
        Returns:
            L'option caster
        """
        if type(option) is str or type(option) is unicode:
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
        """
        Recupere une option et la format au besoin

        Args:
            optionName: Le nom de l'option a retourner
        Returns:
            Valeur de l'option
        """
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

    def getOpenLayersOptions(self):
        """
        Format les options du widget pour OpenLayers

        Returns:
            Les options formatee
        """
        strOptions = "var objOptions = "
        strOptions += self.printOptions() + "; \n"
        strOptions += "objOptions.strategies = []; \n"
        for key, val in self.options.items():
            if key == "projectionString":
                strOptions += "objOptions['projection'] = new OpenLayers.Projection(\"" + val + "\"); \n"
            elif key =="maxExtentString":
                strOptions += "objOptions['maxExtent'] = new OpenLayers.Bounds("+ val +"); \n"
            elif key == "restrictedExtentString":
                strOptions += "objOptions['restrictedExtent'] = new OpenLayers.Bounds("+ val +"); \n"
            elif key == "tileSizeString":
                strOptions += "objOptions['tileSize'] = new OpenLayers.Size("+ val +"); \n"
            elif key == "displayProjectionString":
                strOptions += "objOptions['displayProjection'] = new OpenLayers.Projection(\""+ val +"\"); \n"
            elif key == "resolutionsString":
                strOptions += "objOptions['resolutions'] = ["+val+"]; \n"
            elif key == "scalesString":
                strOptions += "objOptions['scales'] = ["+ val +"]; \n"
            elif key == "cluster":
                strOptions += "objOptions['strategies'].push(new OpenLayers.Strategy.Cluster()); \n"
        return mark_safe(strOptions)

    def hasClones(self):
        return False

    def linkResource(self, user, resourceList):
        """
        Lie les resources au widget

        Args:
            user: L'utilisateur pour valider les droits sur la resource
            resourceList: Liste des resources
        """
        pass

    def addOrReplaceOption(self, resource):
        """
        Remplace ou ajoute une option a partir d'une resource.

        Args:
            resource: La resource ou on recupere l'option
        """
        for key,val in self.getMandatoryResourceOptions().items():
            if resource.getOption(key):
                self.options[val] = resource.options[key]


    def getFormatfromTxt(self, strMsg):
        pattern = re.compile('EPSG:\d+\#?(.*)')
        matches = pattern.search(strMsg)
        if matches:
            return matches.group(1)
        return ""


    def getDisplayProjectionfromTxt(self, strMsg):
        pattern = re.compile('(EPSG:\d+)\#?.*')
        matches = pattern.search(strMsg)
        if matches:
            return matches.group(1)
        return ""

