from geoprisma.models import Service
from proxy import *
from tilecacheproxy import *
from wmsproxy import *
from httprequestproxy import *
from wfsproxy import *
from fileproxy import *
from featureserverproxy import *


def getProxy(service_slug, request):
    """
    Va recuperer le bon proxy selon le service.
    
    Args:
        service_slug: Le slug du service
        request: La requete
    Returns:
        Le proxy s'il y a lieu sinon retourne "no proxy"
    """
    objProxy = None
    objService = Service.objects.getService(service_slug)
    if objService.type.name == "TileCache":
        objProxy = TileCacheProxy(objService, request)
    elif objService.type.name == "WMS":
        objProxy = WMSProxyFactory().getWMSProxy(objService, request)
    elif objService.type.name == "HttpRequest":
        objProxy = HttpRequestProxy(objService, request)
    elif objService.type.name == "WFS":
        objProxy = WFSProxyFactory().getWFSProxy(objService, request)
    elif objService.type.name == "File":
        objProxy = FileProxyFactory().getFileProxy(objService, request)
    elif objService.type.name  == "FeatureServer":
        objProxy = FeatureServerProxyFactory().getFeatureServerProxy(objService, request)

    if not objProxy:
        return "no proxy"
    else:
        return objProxy
 