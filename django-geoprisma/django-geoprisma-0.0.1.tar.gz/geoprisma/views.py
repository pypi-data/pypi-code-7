# coding=utf-8
import urllib2
from .models import Service
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.urlresolvers import reverse
import json
from django.conf import settings
from django.views.generic import View
from core.proxies import getproxy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from functools import wraps
from django.shortcuts import render
from models import Session, Widget, WidgetOption, WidgetType
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from models import Service, Session, Widget, WidgetOption, WidgetType
from django.contrib.auth.models import User, Group
from geoprisma.core.appsession.appsession import AppSession
from geoprisma.core.functions import load_class
from geoprisma.core.resources.resourcebase import ResourceBase
from geoprisma.core.widgets.mappanel import MapPanel
from geoprisma.core.widgets.layer import Layer
from geoprisma.core.widgets.queryonclickwizard import QueryOnClickWizard
from geoprisma.utils import isAuthorized


def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                else:
                    return HttpResponse(status=401)
        return func(request, *args, **kwargs)
    return _decorator

@http_basic_auth
@login_required
@csrf_exempt
def get_proxy(request, *args, **kwargs):
    """
    Vue qui recupere le bon proxy et effectue le traitement demande

    Args:
        request: La requete
        *args: Tableau d'argument
        **kwargs: Tableau d'argument contenant les slugs
    Returns:
        HttpResponse
    """
    service_slug = kwargs.get('service_slug')
    resource_slug = kwargs.get('resource_slug')

    if service_slug:
        proxy = getproxy.getProxy(service_slug, request)
        if resource_slug:
            proxy.getResourcesFromRequest(kwargs)
            proxy.validateResourcesFromRequest()
            proxy.validateLayersFromRequest()
            proxy.areResourcesFromRequestAuthorized()
        return proxy.process()
    return HttpResponse('')


def getAuthorizedResources(user,mapcontextresources):
    """
    Recupere les actions authorises des resources

    Args:
        user: L'utilisateur a valider
        mapcontextresources: La liste des resources
    Returns:
        Liste des actions et liste des noms d'acl
    """
    actionList = ["read", "update", "create", "delete", "export", "read_extended"]
    authorizedResourcesActionsDic = {}
    authorizedResourcesAclNameDic = {}
    for mapcontextresource in mapcontextresources:
        authorizedResourcesActionsDic[mapcontextresource.resource.id] = {}
        for action in actionList:
            if isAuthorized(user, mapcontextresource.resource.name, action):
                authorizedResourcesActionsDic[mapcontextresource.resource.id][action] = True
                authorizedResourcesAclNameDic[mapcontextresource.resource.acl_name] = mapcontextresource.resource.id

    return json.dumps(authorizedResourcesActionsDic), json.dumps(authorizedResourcesAclNameDic)

@login_required
def maprender(request, pwsName=None, pviewId=None, *args, **kwargs):
    """
    Fonction appelee par les applications. Elle genere le context pour le template.

    Args:
        request: Requete django
        pwsName: Le nom du workspace
        pviewId: Id de l'initial view
    Returns:
        context
    """
    #recuperation de l'utilisateur
    try:
        user = User.objects.get(email=request.user)
    except User.DoesNotExist:
        user = User.objects.get(email=request.user.email)

    #Recuperation du workspace
    if pwsName:
        wsName = pwsName
    elif kwargs.get('wsName'):
        wsName = kwargs.get('wsName')
    else:
        raise Exception("No workspace")

    #Recuperation du viewid
    if pviewId:
        viewId = pviewId
    elif kwargs.get('viewId'):
        viewId = kwargs.get('viewId')
    else:
        viewId = ""

    if wsName:
        session = Session.objects.select_related().get(name=wsName)

    # Defini l'url de base pour le proxy en php
    baseUrl = "/"

    authorizedResourcesActions, authorizedResourcesAclName = getAuthorizedResources(user,session.mapContext.mapcontextresource_set.all())

    #Cree l'objet session qui va gerer la recuperation de widget
    appSession = AppSession()

    #Ajout api a la liste des type de widget utiliser
    appSession.widgetTypeSet.add("api")

    #Cree le widget mappanel a partir du map context
    mapWidget = MapPanel(session.mapContext)
    appSession.widgetList.append(mapWidget)
    appSession.widgetTypeSet.add("mappanel")

    # Boucle dans les resources pour les initialiser
    for mapContextResource in session.mapContext.mapcontextresource_set.all():
        #Verifie le droit de lecture sur la resource
        if isAuthorized(user,mapContextResource.resource.name, "read"):
            #Ajoute la resource a la liste des resources
            resource = ResourceBase(mapContextResource.resource)
            appSession.resourceList.append(resource)

    # Boucle dans les widgets de l'application
    widgetList = []
    for applicationWidget in session.application.applicationwidget_set.all():
        widgetClass = load_class(applicationWidget.widget.type.classname)
        widget = widgetClass(applicationWidget.widget)
        widget.linkResource(user, appSession.resourceList)
        #Valide si on ajoute le widget ou non
        if widget.toAdd:
            # Ajout de l'initialview directement pour l'ordre des widgets
            # Corrige ainsi le bug de l'autozoom
            if widget.type.name.lower() == "initialview":
                appSession.widgetList.append(widget)
            elif widget.hasClones():
                widgetList.extend(widget.getClones())
            else:
                widgetList.append(widget)
            if widget.type.name.lower() == "queryonclickwizard":
                appSession.widgetTypeSet.add("queryonclick")
                appSession.widgetTypeSet.add("resultvectorlayer")
                for subwidget in widgetList:
                    if subwidget.type.name.lower() == "geoexttoolbar":
                        subwidget.options["widgets"].insert(0,"__separator__")
                        subwidget.options["widgets"].insert(0,"W_MyQueryOnClick")
                        break
            appSession.widgetTypeSet.add(widget.type.name.lower())

    # Construction des couches
    layerList = []
    for resource in appSession.resourceList:
        for datastore in resource.datastores.all().order_by("service__type__priority"):
            if datastore.service.type.name == "WMS":
                if not resource.getDatastoreByType("TileCache") and not resource.getDatastoreByType("TMS"):
                    layerWidget = Layer(resource, "WMS")
                    layerList.append(layerWidget)
            elif datastore.service.type.name == "TileCache" or datastore.service.type.name == "GYMO" or datastore.service.type.name == "TMS":
                layerWidget = Layer(resource, datastore.service.type.name)
                layerList.append(layerWidget)
            elif datastore.service.type.name == "FeatureServer" or datastore.service.type.name == "WFS":
                if resource.hasWidgetUsingServiceType(datastore.service.type.name) or resource.datastores.count() == 1:
                    layerWidget = Layer(resource, datastore.service.type.name)
                    layerList.append(layerWidget)

    # Append widgetLayerList and widgetList to the appSession widgetList in order
    appSession.widgetList.extend(layerList)
    appSession.widgetList.extend(widgetList)

    renderContext = {'widgets':appSession.widgetList,
                   'widgetTypeSet':appSession.widgetTypeSet,
                   'resources':appSession.resourceList,
                   'appSession':appSession,
                   'mapName':session.mapContext.name,
                   'wsName':session.name,
                   'viewId':viewId,
                   'templateName':session.application.template,
                   'authorizedActions': authorizedResourcesActions,
                   'authorizedResourcesAclName': authorizedResourcesAclName,
                   'drawMode':session.application.type.name.lower(),
                   'baseUrl':baseUrl,
                   'user': user
                   }

    return renderContext









