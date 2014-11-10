import proxy
import urllib
import urllib2
import requests
from django.http import HttpResponse


class TileCacheProxy(proxy.Proxy):
    """
    Class TileCacheProxy

    """

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        """
        Traite l'information a retourner

        Returns:
            HttpResponce
        """
        excluded_headers = ('connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','transfer-encoding','upgrade','content-encoding','content-length')

        if self.m_objRequest.GET.get("staticCache"):
            strRequestURL = self.addParam(self.m_objService.source).replace("?staticCache", "")
            requestUrl = requests.get(strRequestURL)
        else:
            strRequestURL = self.addParam(self.m_objService.source)
            requestUrl = requests.get(strRequestURL)

        responce = HttpResponse(requestUrl)
        for header in requestUrl.headers:
            if header not in excluded_headers:
                responce[header] = requestUrl.headers.get(header)

        return responce

    def getLayers(self):
        """
        Recupere les couches

        Returns:
            Tableau de couche
        """
        objArrayLayer = []
        bLayersFound = False
        for (strKey, strValue) in self.m_objRequest.GET.iteritems():
            if strKey.upper() == "LAYERS":
                bLayersFound = True
                break
        if bLayersFound and self.m_objRequest.GET.get(strKey):
            objArrayLayer = self.m_objRequest.GET.get(strKey).split(",")
        elif self.m_objRequest.GET.get('staticCache'):
            objArrayPathInfo = self.m_objRequest.GET.get('staticCache').split("/")
            objArrayLayer.append(objArrayPathInfo[1])

        return objArrayLayer

