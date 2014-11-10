import urllib
import requests
from geoprisma.utils import isAuthorized
from geoprisma.models import Resource, Datastore
from django.contrib.auth.models import User


class Proxy(object):
    """
    Class Proxy de base.
    Tout les autres proxy herite de cette classe.

    """

    CRUD_CREATE = "create"
    CRUD_READ = "read"
    CRUD_UPDATE = "update"
    CRUD_DELETE = "delete"

    def __init__(self, service, prequest):
        """
        Constructeur

        Args:
            service: Le service
            prequest: La requete
        """
        self.m_objService = service
        self.m_objRequest = prequest
        self.m_objResource = []

    #def setResources(self, pobjArrayResources):
    #   self.m_objResource = pobjArrayResources

    def getLayers(self):
        pass

    def addParam(self, pstrUrl):
        """
        Ajoute des parametres a un url.

        Args:
            pstrUrl: L'url
        Returns:
            un Url
        """
        if '?' in pstrUrl:
            return pstrUrl+"&"+urllib.urlencode(self.getRequestParams())
        else:
            return pstrUrl+"?"+urllib.urlencode(self.getRequestParams())

    def getPathInfo(self):
        """
        Recupere le pathinfo.

        Return:
            Le path info
        """
        if self.m_objRequest.path_info:
            return self.m_objRequest.path_info
        return ''

    def getRequestParams(self):
        """
        Recupere les parametres du querystring.

        Returns:
            Un tableau contenant les parametres
        """
        objArrayParams = {}
        for (strKey, strParam) in self.m_objRequest.GET.iteritems():
            if strKey[:3] != "osm":
                objArrayParams[strKey] = strParam

        return objArrayParams

    def getResourcesFromRequest(self, pobjConfig, pobjRequest=None):
        if pobjRequest:
            objRequest = pobjRequest
        else:
            objRequest = pobjConfig

        if objRequest.get('service_slug') is None:
            raise Exception("osmservice param is missing")

        if objRequest.get('resource_slug') is list:
            pass
        else:
            self.m_objResource.append(Resource.objects.getResource(objRequest.get('resource_slug')))

    def validateResourcesFromRequest(self, pobjService=None, pobjArrayResources=None):
        """
        Valide si la resources est valide avec le service.

        Args:
            pobjService: Object service optionnel
            pobjArrayResources: Object Resource optionnel
        Raise:
            Exception: Not Authorized by config - Service
        """
        if pobjService is None:
            objService = self.m_objService
        else:
            objService = pobjService

        if pobjArrayResources is None:
            objArrayResources = self.m_objResource
        else:
            objArrayResources = pobjArrayResources

        for objResource in objArrayResources:
            if not objResource.datastores.filter(service=objService):
                raise Exception('Not Authorized by Config - Service')

    def validateLayersFromRequest(self, pobjService=None, pobjArrayResources=None, pobjArrayLayers=None):
        """
        Valide les couches d'une requete.

        Args:
            pobjService: Object service optionnel
            pobjArrayResources: Object resource optionnel
            pobjArrayLayers: Object couche optionnel
        Raise:
            Exception: Not Authorized by Datastore layer
        """
        if pobjService is None:
            objService = self.m_objService
        else:
            objService = pobjService

        if pobjArrayResources is None:
            objArrayResource = self.m_objResource
        else:
            objArrayResource = pobjArrayResources

        if pobjArrayLayers is None:
            objArraylayers = self.getLayers()
        else:
            objArraylayers = pobjArrayLayers

        bAllAuthorized = True
        for strLayer in objArraylayers:
            bIsAuthorized = False
            for objResource in self.m_objResource:
                objDatastore = objResource.datastores.filter(service=objService)
                if objDatastore.filter(layers__contains=strLayer):
                    bIsAuthorized = True
                    break
            if not bIsAuthorized:
                bAllAuthorized = False
                break
        if not bAllAuthorized:
            raise Exception('Not Authorized by Datastore layer')

    def areResourcesFromRequestAuthorized(self, pobjArrayResources=None):
        if pobjArrayResources is None:
            objArrayResource = self.m_objResource
        else:
            objArrayResource = pobjArrayResources

        try:
            user = User.objects.get(id=self.m_objRequest.user.pk)
        except User.DoesNotExist:
            raise Exception("Authentification required")

        for objResource in objArrayResource:
            if not isAuthorized(user, objResource.name, self.getAction()):
                raise Exception("Not Authorized by ACL")





