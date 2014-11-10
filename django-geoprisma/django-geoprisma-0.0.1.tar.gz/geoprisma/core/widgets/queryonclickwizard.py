from geoprisma.utils import isAuthorized
from geoprisma.models import WidgetType
from widgetbase import WidgetBase
from queryonclick import QueryOnClick
from resultvectorlayer import ResultVectorLayer

class QueryOnClickWizard(WidgetBase):
    """
    QueryOnClickWizard
    """

    def __init__(self, widgetModel):
        super(QueryOnClickWizard,self).__init__(widgetModel)
        self.queryOnClickWidget = None
        self.resultVectorLayerWidget = None
        self.vectorLayerWidget = None

    def getServiceType(self):
        return "wms"

    def needLayer(self):
        return True

    def hasClones(self):
        return True

    def linkResource(self, user, resourceList):
        self.resourceList = resourceList
        self.user = user
        for resource in self.resourceList:
            if resource.getOption("queryable"):
                if isAuthorized(user, resource.name, self.action):
                    if not self.queryOnClickWidget:
                        self.setVectorLayerWidget()
                        self.setResultVectorLayerWidget()
                        self.setQueryOnClickWidget()
                    resource.addWidget(self.queryOnClickWidget)
                    resource.addWidget(self.resultVectorLayerWidget)


    def setVectorLayerWidget(self):
        vectorLayerWidget = WidgetBase()
        vectorLayerWidget.id = "W_MyVectorLayer"
        vectorLayerWidget.name = ""
        vectorLayerWidget.type = WidgetType(name="vectorlayer")
        vectorLayerWidget.action = "read"
        vectorLayerWidget.options = {
            "displayInLayerSwitcher" : False,
        }

        if self.getOption("layerName"):
            vectorLayerWidget.options['title'] = self.getOption("layerName")

        self.vectorLayerWidget = vectorLayerWidget

    def setResultVectorLayerWidget(self):
        resultVectorLayerWidget = ResultVectorLayer()
        resultVectorLayerWidget.id = "W_MyResultVectorLayer"
        resultVectorLayerWidget.name = ""
        resultVectorLayerWidget.type = WidgetType(name="resultvectorlayer")
        resultVectorLayerWidget.action = "read"
        resultVectorLayerWidget.options = {
            "vectorlayer" : self.vectorLayerWidget.id,
            "singleMode" : True
        }
        resultVectorLayerWidget.linkResource(self.user, self.resourceList)
        self.resultVectorLayerWidget = resultVectorLayerWidget

    def setQueryOnClickWidget(self):
        queryOnClickWidget = QueryOnClick()
        queryOnClickWidget.id = "W_MyQueryOnClick"
        queryOnClickWidget.name = ""
        queryOnClickWidget.type = WidgetType(name="queryonclick")
        queryOnClickWidget.action = "read"
        queryOnClickWidget.options =  {
            "dropDownList" : False,
            "multipleKey" : "shiftKey",
            "noMarker" : True,
            "results" : self.resultVectorLayerWidget.id,
            "toggle" : True,
            "displayClass" : "olControlQueryOnClickWizard"
        }
        if self.getOption("iconCls"):
            queryOnClickWidget.options['iconCls'] = self.getOption("iconCls")
        else:
            queryOnClickWidget.options['iconCls'] = "queryonclickwizard"

        queryOnClickWidget.linkResource(self.user, self.resourceList)
        self.queryOnClickWidget = queryOnClickWidget

    def getClones(self):
        if self.queryOnClickWidget:
            return [self.vectorLayerWidget, self.queryOnClickWidget, self.resultVectorLayerWidget]
        else:
            return []
