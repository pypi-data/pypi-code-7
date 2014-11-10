import re
import copy
from widgetbase import WidgetBase
from geoprisma.models import WidgetType
from django.utils.safestring import mark_safe


class Layer(WidgetBase):
    """
    Layer
    """
    def __init__(self,resourceModel, serviceType=None):
        self.name = resourceModel.name
        self.slug = resourceModel.slug
        self.type = WidgetType(name="layer")
        self.action = "read"
        try:
            self.datastore = resourceModel.datastores.filter(service__type__name__iexact=serviceType)[0]
        except IndexError:
            pass
        self.resource = resourceModel
        self.options = self.setOptions(copy.deepcopy(resourceModel.options))
        self.id = "layer_S" + str(self.datastore.service.id) + "_DS" + str(self.datastore.id) + "_R" + str(self.resource.id)

    def setOptions(self, options):
        optionDic = {}
        for option in self.datastore.service.type.defaultlayeroption_set.all():
            optionDic[option.name] = self.castOption(option.value)
        optionDic["servicetype"] = self.datastore.service.type.name.lower()
        # Regex pour recuperer les options de la resource selon le datastore
        pattern = re.compile(self.datastore.service.type.name.lower())
        for key in options.keys():
            matches = pattern.search(key)
            if matches:
                newKey =  key.replace(matches.group(0),"",1)
                optionDic[newKey] = options.pop(key)
                # Supprime la valeur actuel de la clef trouvee dans le cas de doublon
                try:
                    options.pop(newKey)
                except KeyError:
                    pass
        optionDic.update(options)
        return optionDic

    def printLayerURL(self):
        """
        Construit l'url d'une couche

        Returns:
            L'url formate
        """
        strUrl = """
        var objArrayURLParams = [];
          objArrayURLParams.push();

          var objURLParams = {
              'osmservice': '"""+str(self.datastore.service.id)+"""'
          };
          var strParams = OpenLayers.Util.getParameterString(objURLParams);
          strParams += '&osmresource[]="""+str(self.resource.id)+"""';
          if(strParams.length > 0) {
              var strSeparator = (strURL.indexOf('?') > -1) ? '&' : '?';
              strURL += strSeparator + strParams;
              for(var i=0; i<objArrayURLAliases.length; i++){
                  var strSeparator = (objArrayURLAliases[i].indexOf('?') > -1) ? '&' : '?';
                  objArrayURLAliases[i] += strSeparator + strParams;
              }
          }
          """
        return mark_safe(strUrl)

    def printLayerDjangoURL(self):
        """
        Construit l'url d'une couche appelant le proxy geoprisma django.

        Returns:
            L'url formate
        """
        strUrl = """
        var objArrayURLParams = [];
          objArrayURLParams.push();
          objArrayURLAliases = [strDjangoURL];
          var strParams = '"""+self.datastore.service.slug+"""/"""+self.resource.slug.lower()+"""';
          if(strParams.length > 0) {
              for(var i=0; i<objArrayURLAliases.length; i++){
                  var strSeparator = (objArrayURLAliases[i].indexOf('?') > -1) ? '&' : '?';
                  objArrayURLAliases[i] += strParams;
              }
          }
          """
        return mark_safe(strUrl)


    def getWMSParams(self):
        """
        Recupere le parametres WMS d'un widget

        Returns:
            Les parametres formates
        """
        strParams = "var objParams = {'layers': ['"+self.datastore.layers+"'] };"

        try:
            option = self.datastore.service.serviceoption_set.filter(name="version")
            strParams += "objParams[\"version\"] = '"+option[0].value+"';"
            if option[0].value == "1.3.0":
                strParams += 'objParams["exceptions"] = "INIMAGE";'
        except IndexError:
            pass

        if self.getOption("format"):
            strParams += 'objParams["format"] = "'+self.getOption("format")+'";'
        if self.getOption("maxfeatures"):
            strParams += 'objParams["maxfeatures"] = "'+self.getOption("maxfeatures")+'";'
        if self.getOption("transparent"):
            strParams += 'objParams["transparent"] = "'+self.getOption("transparent")+'";'
        if self.getOption("typename"):
            strParams += 'objParams["typename"] = "'+self.getOption("typename")+'";'

        return mark_safe(strParams)

