import proxy
import requests
import re
from django.http import HttpResponse


class FeatureServerProxy(proxy.Proxy):
    PATH_INFO_REG = '/^\/([a-zA-Z0-9_]+)\/?(([0-9]*|all)\.?(GeoJSON|json|kml|atom|gml)?)$/i'
    PATH_INFO_LAYER_POS = 1
    PATH_INFO_ID_POS  = 3

    def getLayer(self):
        strPathInfo = self.getPathInfo()
        objMatches = re.search(self.PATH_INFO_REG, strPathInfo)
        if objMatches:
            return objMatches.group(self.PATH_INFO_LAYER_POS)
        else:
            return ''


    def getID(self):
        strPathInfo = self.getPathInfo()
        objMatches = re.search(self.PATH_INFO_REG, strPathInfo)
        if objMatches and len(objMatches) >= self.PATH_INFO_ID_POS:
            dataId = objMatches.group(self.PATH_INFO_ID_POS)
            if dataId.isdigit():
                return int(dataId)
        else:
            return None


    def getLayers(self):
        objLayerList = []
        strLayer = self.getLayer()
        if strLayer != "":
            objLayerList.append(strLayer)
        return objLayerList


class FeatureServerGetCapabilityProxy(FeatureServerProxy):

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        url = self.addParam(self.self.m_objService.source)
        requestUrl = requests.post(url)
        return HttpResponse(requestUrl)


class FeatureServerReadProxy(FeatureServerProxy):

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        strPathInfo = self.getPathInfo()
        url = self.addParam(self.self.m_objService.source + strPathInfo)
        requestUrl = requests.get(url)
        return HttpResponse(requestUrl)


class FeatureServerCreateProxy(FeatureServerProxy):

    def getAction(self):
        return self.CRUD_CREATE

    def process(self):
        strPathInfo = self.getPathInfo()
        url = self.addParam(self.mm_objService.source + strPathInfo)
        requestUrl = requests.post(url, data=self.m_objRequest.body)
        return HttpResponse(requestUrl)



class FeatureServerUpdateProxy(FeatureServerProxy):

    def getAction(self):
        return self.CRUD_UPDATE

    def process(self):
        strPathInfo = self.getPathInfo()
        url = self.addParam(self.mm_objService.source + strPathInfo)
        requestUrl = requests.put(url , data=self.m_objRequest.body)
        return HttpResponse(requestUrl)


class FeatureServerDeleteProxy(FeatureServerProxy):

    def getAction(self):
        return self.CRUD_DELETE

    def process(self):
        strPathInfo = self.getPathInfo()
        url = self.addParam(self.mm_objService.source + strPathInfo)
        requestUrl = requests.delete(url)
        return HttpResponse(requestUrl)


class FeatureServerProxyFactory(object):
    """
    Retourne le bon feature server proxy
    """

    def getFeatureServerProxy(self, pobjService, prequest):
        self.request = prequest
        self.featureServerProxy = FeatureServerProxy(pobjService, prequest)

        if self.isGetCapability():
            return FeatureServerGetCapabilityProxy(pobjService, prequest)
        elif self.isDelete():
            return FeatureServerDeleteProxy(pobjService, prequest)
        elif self.isUpdate():
            return FeatureServerUpdateProxy(pobjService, prequest)
        elif self.isCreate():
            return FeatureServerCreateProx(pobjService, prequest)
        else:
            return FeatureServerReadProxy(pobjService, prequest)




    def isGetCapability(self):
        """
        Check if query is the type of getCapability | The layer is not specifield
        """
        strLayer = self.featureServerProxy.getLayer()
        return strLayer == ""


    def isDelete(self):
        data_id = self.featureServerProxy.getID()
        return data_id != None and self.request.method == "DELETE"


    def isCreate(self):
        data_id = self.featureServerProxy.getID()
        return data_id != None and self.request.body != "" and self.request.method == "POST"


    def isUpdate(self):
        data_id = self.featureServerProxy.getID()
        return data_id != None and request.method == "PUT"
