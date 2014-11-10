# -*- coding: utf-8 -*-
import proxy
import urllib
import requests
from django.conf import settings
from django.http import HttpResponse
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from django.contrib.auth.models import User
from geoprisma.utils import isAuthorized
from geoprisma.models import Datastore
from django.db.models import Q


class WMSProxyFactory(object):
    """
    Un proxy factory pour le WMS qui retourne le bon proxy WMS selon l'operation demande.

    """
    WMS_OP_GETCAPABILITIES = 1
    WMS_OP_GETMAP = 2
    WMS_OP_GETLEGENDGRAPHIC = 3
    WMS_OP_GETFEATUREINFO = 4


    def getWMSProxy(self, pobjService, prequest):
        """
        Recupere le proxy selon l'operation

        Args:
            pobjService: Object service
            prequest: La requete
        Returns:
            Un proxy WMS
        """
        iOPType = self.getOperationFromGET(prequest)

        objWMSProxy = None
        if iOPType == self.WMS_OP_GETCAPABILITIES:
            objWMSProxy = WMSGetCapabilityProxy(pobjService, prequest)
        elif iOPType == self.WMS_OP_GETMAP:
            objWMSProxy = WMSProxy(pobjService, prequest)
        elif iOPType == self.WMS_OP_GETLEGENDGRAPHIC:
            objWMSProxy = WMSProxy(pobjService, prequest)
        elif iOPType == self.WMS_OP_GETFEATUREINFO:
            objWMSProxy = WMSProxy(pobjService, prequest)

        if objWMSProxy is None:
            raise Exception("Proxy method not handled.")

        return objWMSProxy

    def getOperationFromGET(self, prequest):
        """
        Recupere l'operation dans l'url

        Args:
            prequest: La requete contenant l'url
        Returns:
            l'operation
        """
        strRequest = ''
        for (strKey, strValue) in prequest.GET.iteritems():
            if strKey.upper() == 'REQUEST':
                strRequest = strValue
                break
        if strRequest == 'GetCapabilities':
            return self.WMS_OP_GETCAPABILITIES
        elif strRequest == 'GetMap':
            return self.WMS_OP_GETMAP
        elif strRequest == 'GetLegendGraphic':
            return self.WMS_OP_GETLEGENDGRAPHIC
        elif strRequest == 'GetFeatureInfo':
            return self.WMS_OP_GETFEATUREINFO
        return None

class WMSProxy(proxy.Proxy):
    """
    Class WMSProxy qui herite de la class proxy de base

    """

    def getAction(self):
        return self.CRUD_READ

    def setResources(self, pobjArrayResources):
        """
        Defini la resource du proxy

        Args:
            pobjArrayResources: Object resource
        """
        self.m_objResource = pobjArrayResources

    def process(self):
        """
        Traite l'information a retourner

        Returns:
            HttpResponce
        """
        excluded_headers = ('connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','transfer-encoding','upgrade')

        if self.m_objRequest.method == "POST":
            strServiceURL = self.m_objService.source
            strParams = self.getRequestParams()
            requestUrl = requests.post(strServiceURL, data=strParams)

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
            Un tableau de couches
        """
        objArrayLayer = []
        for (strKey, strValue) in self.m_objRequest.GET.iteritems():
            if strKey.upper() == "LAYERS":
                objArrayLayer = self.m_objRequest.GET.get(strKey).split(",")

        return objArrayLayer

    def getCaching(self):
        pass

class WMSGetCapabilityProxy(proxy.Proxy):
    """
    Class WMSGetCapabilityProxy qui traite seulement le getCapabilities

    """

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        """
        Fonction qui recupere le XML retourne par mapserver le decoupe selon les droits de l'utilisateur.
        Chaque version de WMS est traite differament.

        Returns:
            HttpResponce
        """
        excluded_headers = ('connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','transfer-encoding','upgrade','content-encoding','content-length')
        url = self.addParam(self.m_objService.source)
        requestUrl = requests.get(url)
        objXml = ET.fromstring(requestUrl.text.encode("utf-8"))
        docinfo = objXml.getroottree().docinfo
        wmsversion = objXml.get("version")
        user = User.objects.get(email=self.m_objRequest.user)
        # Gestion des sandbox
        baseUrl = ""
        if hasattr(settings, 'DEBUG_APP_URL') and settings.DEBUG_APP_URL:
            baseUrl = settings.DEBUG_APP_URL
        onlineResourceUrl = "http://"+self.m_objRequest.get_host()+baseUrl+"/gp/proxy/"+self.m_objService.slug+""

        def changeUrl(url):
            """
            Convertie l'url du XMl pour correspondre a l'url de geoprisma

            """
            splitUrl = url.split("&",1)
            newUrl = onlineResourceUrl+"?"+splitUrl[1]
            return newUrl

        def getAndValidateRes(layer,removeList):
            """
            Recupere les resources d'un datastore et verifie les droits de l'utilisateur

            Args:
                layer: la couche pour aider a trouver le datastore
                removeList: une liste ou on ajoute les couches non authorisees
            """
            if wmsversion == "1.0.0" or wmsversion == "1.1.0" or wmsversion == "1.1.1":
                layerName = layer.find('Name')
            else:
                layerName = layer.find("{http://www.opengis.net/wms}Name")

            try:
                datastore = Datastore.objects.get(service=self.m_objService, layers=layerName.text)
                dataResourceList = datastore.resource_set.all()
                for resource in dataResourceList:
                    if isAuthorized(user, resource.name,"read"):
                        break
                    else:
                        removeList.append(layer)
            except Datastore.DoesNotExist:
                removeList.append(layer)

        #WMS VERSION 1.0.0
        if wmsversion == "1.0.0":
            for elem in objXml:
                if elem.tag == "Service":
                    onlineRes = elem.find("OnlineResource")
                    onlineRes.text = onlineResourceUrl
                if elem.tag == "Capability":
                    removeCapabilityList = list()
                    for capability in elem:
                        if capability.tag == "Request":
                            for request in capability:
                                httptag = request.find("DCPType").find("HTTP")
                                for method in httptag:
                                    method.set("onlineResource",onlineResourceUrl)
                        if capability.tag == "Layer":
                            removeGroupList = list()
                            for layerGroup in capability:
                                removeList = list()
                                if layerGroup.tag == "Layer":
                                    layerList = layerGroup.findall("Layer")
                                    for layer in layerList:
                                        if layer.tag == "Layer":
                                            getAndValidateRes(layer, removeList)
                                    for layer in removeList:
                                        layerGroup.remove(layer)
                                    filtredLayerList = layerGroup.findall("Layer")
                                    if filtredLayerList.__len__() == 0:
                                        getAndValidateRes(layerGroup,removeGroupList)
                                    else:
                                        for layer in filtredLayerList:
                                            layerStyle = layer.find("Style")
                                            if layerStyle is not None:
                                                legendUrl = layerStyle.find("LegendURL")
                                                legendOnlineRes = legendUrl.find("OnlineResource")
                                                newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                                legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                            for layer in removeGroupList:
                                try:
                                    capability.remove(layer)
                                except ValueError:
                                    pass
                            capabilityList = capability.findall("Layer")
                            if capabilityList.__len__() == 0:
                                getAndValidateRes(capability,removeCapabilityList)
                            else:
                                for layer in capabilityList:
                                    layerStyle = layer.find("Style")
                                    if layerStyle is not None:
                                        legendUrl = layerStyle.find("LegendURL")
                                        legendOnlineRes = legendUrl.find("OnlineResource")
                                        newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                        legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                        for capability in removeCapabilityList:
                            elem.remove(capability)
        #WMS VERSION 1.1.0
        if wmsversion == "1.1.0":
            for elem in objXml:
                if elem.tag == "Service":
                    onlineRes = elem.find("OnlineResource")
                    onlineRes.text = onlineResourceUrl
                if elem.tag == "Capability":
                    removeCapabilityList = list()
                    for capability in elem:
                        if capability.tag == "Request":
                            for request in capability:
                                httptag = request.find("DCPType").find("HTTP")
                                for method in httptag:
                                    onlineRes = method.find("OnlineResource")
                                    onlineRes.set("{http://www.w3.org/1999/xlink}href",onlineResourceUrl)
                        if capability.tag == "Layer":
                            removeGroupList = list()
                            for layerGroup in capability:
                                removeList = list()
                                if layerGroup.tag == "Layer":
                                    layerList = layerGroup.findall("Layer")
                                    for layer in layerList:
                                        if layer.tag == "Layer":
                                            getAndValidateRes(layer, removeList)
                                    for layer in removeList:
                                        layerGroup.remove(layer)
                                    filtredLayerList = layerGroup.findall("Layer")
                                    if filtredLayerList.__len__() == 0:
                                        getAndValidateRes(layerGroup,removeGroupList)
                                    else:
                                        for layer in filtredLayerList:
                                            layerStyle = layer.find("Style")
                                            if layerStyle is not None:
                                                legendUrl = layerStyle.find("LegendURL")
                                                legendOnlineRes = legendUrl.find("OnlineResource")
                                                newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                                legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                            for layer in removeGroupList:
                                try:
                                    capability.remove(layer)
                                except ValueError:
                                    pass
                            capabilityList = capability.findall("Layer")
                            if capabilityList.__len__() == 0:
                                getAndValidateRes(capability,removeCapabilityList)
                            else:
                                for layer in capabilityList:
                                    layerStyle = layer.find("Style")
                                    if layerStyle is not None:
                                        legendUrl = layerStyle.find("LegendURL")
                                        legendOnlineRes = legendUrl.find("OnlineResource")
                                        newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                        legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                        for capability in removeCapabilityList:
                            elem.remove(capability)
        # WMS VERSION 1.1.1
        elif wmsversion == "1.1.1":
            for elem in objXml:
                if elem.tag == "Service":
                    onlineRes = elem.find("OnlineResource")
                    onlineRes.set("{http://www.w3.org/1999/xlink}href",onlineResourceUrl)
                if elem.tag == "Capability":
                    removeCapabilityList = list()
                    for capability in elem:
                        if capability.tag == "Request":
                            for request in capability:
                                httptag = request.find("DCPType").find("HTTP")
                                for method in httptag:
                                    onlineRes = method.find("OnlineResource")
                                    onlineRes.set("{http://www.w3.org/1999/xlink}href",onlineResourceUrl)
                        if capability.tag == "Layer":
                            removeGroupList = list()
                            for layerGroup in capability:
                                removeList = list()
                                if layerGroup.tag == "Layer":
                                    layerList = layerGroup.findall("Layer")
                                    for layer in layerList:
                                        if layer.tag == "Layer":
                                            getAndValidateRes(layer, removeList)
                                    for layer in removeList:
                                        layerGroup.remove(layer)
                                    filtredLayerList = layerGroup.findall("Layer")
                                    if filtredLayerList.__len__() == 0:
                                        getAndValidateRes(layerGroup,removeGroupList)
                                    else:
                                        for layer in filtredLayerList:
                                            layerStyle = layer.find("Style")
                                            if layerStyle is not None:
                                                legendUrl = layerStyle.find("LegendURL")
                                                legendOnlineRes = legendUrl.find("OnlineResource")
                                                newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                                legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                            for layer in removeGroupList:
                                try:
                                    capability.remove(layer)
                                except ValueError:
                                    pass
                            capabilityList = capability.findall("Layer")
                            if capabilityList.__len__() == 0:
                                getAndValidateRes(capability,removeCapabilityList)
                            else:
                                for layer in capabilityList:
                                    layerStyle = layer.find("Style")
                                    if layerStyle is not None:
                                        legendUrl = layerStyle.find("LegendURL")
                                        legendOnlineRes = legendUrl.find("OnlineResource")
                                        newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                        legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                        for capability in removeCapabilityList:
                            elem.remove(capability)
        #WMS VERSION 1.3.0
        elif wmsversion == "1.3.0":
            schemaLocation = objXml.get("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation")
            schemaLocationList = schemaLocation.split(" ")
            schemaLocationList[-1] = changeUrl(schemaLocationList[-1])
            objXml.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"," ".join(schemaLocationList))
            for elem in objXml:
                if elem.tag == "{http://www.opengis.net/wms}Service":
                    onlineRes = elem.find("{http://www.opengis.net/wms}OnlineResource")
                    onlineRes.set("{http://www.w3.org/1999/xlink}href",onlineResourceUrl)
                if elem.tag == "{http://www.opengis.net/wms}Capability":
                    removeCapabilityList = list()
                    for capability in elem:
                        if capability.tag == "{http://www.opengis.net/wms}Request":
                            for request in capability:
                                httptag = request.find("{http://www.opengis.net/wms}DCPType").find("{http://www.opengis.net/wms}HTTP")
                                for method in httptag:
                                    onlineRes = method.find("{http://www.opengis.net/wms}OnlineResource")
                                    onlineRes.set("{http://www.w3.org/1999/xlink}href",onlineResourceUrl)
                        if capability.tag == "{http://www.opengis.net/wms}Layer":
                            removeGroupList = list()
                            for layerGroup in capability:
                                removeList = list()
                                if layerGroup.tag == "{http://www.opengis.net/wms}Layer":
                                    layerList = layerGroup.findall("{http://www.opengis.net/wms}Layer")
                                    for layer in layerList:
                                        if layer.tag == "{http://www.opengis.net/wms}Layer":
                                            getAndValidateRes(layer, removeList)
                                    for layer in removeList:
                                        layerGroup.remove(layer)
                                    filtredLayerList = layerGroup.findall("{http://www.opengis.net/wms}Layer")
                                    if filtredLayerList.__len__() == 0:
                                        getAndValidateRes(layerGroup,removeGroupList)
                                    else:
                                        for layer in filtredLayerList:
                                            layerStyle = layer.find("{http://www.opengis.net/wms}Style")
                                            if layerStyle is not None:
                                                legendUrl = layerStyle.find("{http://www.opengis.net/wms}LegendURL")
                                                legendOnlineRes = legendUrl.find("{http://www.opengis.net/wms}OnlineResource")
                                                newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                                legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                            for layer in removeGroupList:
                                try:
                                    capability.remove(layer)
                                except ValueError:
                                    pass
                            capabilityList = capability.findall("{http://www.opengis.net/wms}Layer")
                            if capabilityList.__len__() == 0:
                                getAndValidateRes(capability,removeCapabilityList)
                            else:
                                for layer in capabilityList:
                                    layerStyle = layer.find("{http://www.opengis.net/wms}Style")
                                    if layerStyle is not None:
                                        legendUrl = layerStyle.find("{http://www.opengis.net/wms}LegendURL")
                                        legendOnlineRes = legendUrl.find("{http://www.opengis.net/wms}OnlineResource")
                                        newLegendOnlineResUrl = changeUrl(legendOnlineRes.get("{http://www.w3.org/1999/xlink}href"))
                                        legendOnlineRes.set("{http://www.w3.org/1999/xlink}href",newLegendOnlineResUrl)
                        for capability in removeCapabilityList:
                            elem.remove(capability)


        responce = HttpResponse(ET.tostring(objXml, xml_declaration=True, encoding=docinfo.encoding))
        #responce = HttpResponse(requestUrl)
        for header in requestUrl.headers:
            if header not in excluded_headers:
                responce[header] = requestUrl.headers.get(header)
        responce['content-type'] = "text/xml"
        return responce



