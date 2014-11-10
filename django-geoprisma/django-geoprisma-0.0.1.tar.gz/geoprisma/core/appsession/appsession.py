from geoprisma.models import Service, Datastore

class AppSession(object):
    """
    Objet session qui fait des manipulations dans les templates
    """

    def __init__(self):
        self.widgetList = []
        self.widgetTypeSet = set()
        self.resourceList = []

    def getObjectOption(self, elem, optionName):
        """
        Recupere une ou des option pour l'assigner dans le template

        Args:
            elem: L'objet avec les options
            optionName: Le nom de l'option
        Returns:
            La valeur de ou des l'options
        """
        option = []
        if isinstance(elem, Service):
            option = elem.serviceoption_set.filter(name=optionName).values_list('value', flat=True)
        elif isinstance(elem, Datastore):
            option = elem.datastoreoption_set.filter(name=optionName).values_list('value', flat=True)
        try:
            if len(option) > 1:
                return option
            else:
                return option[0]
        except IndexError:
            return False

    def getWidgetById(self, widgetId):
        for widget in self.widgetList:
            if widget.id == widgetId:
                return widget

    def getWidgetByType(self, widgetType):
        for widget in self.widgetList:
            if widget.type.name.lower() == widgetType:
                return widget

    def getWidgetArrayByType(self, widgetType):
        widgetList = []
        for widget in self.widgetList:
            if widget.type.name.lower() == widgetType:
                widgetList.append(widget)
        return widgetList

    def getWidgetByName(self, widgetName):
        for widget in self.widgetList:
            if widget.name == widgetName or widget.id == widgetName:
                return widget

    def getWidgetByOption(self, optionName):
        """
        Recupere un ou des widgets selon une option

        Args:
            optionName: Le nom de l'option
        Returns:
            Tableau de widgets
        """
        for widget in self.widgetList:
                if widget.getOption(optionName):
                    return widget
        else:
            return False

    def getWidgetsByOptionValue(self, optionName,optionValue):
        """
        Recupere un ou des widgets selon une option et sa valeur pour l'assigner dans le template

        Args:
            optionName: Le nom de l'option
            optionValue: la valeur de l'option
        Returns:
            Tableau de widgets
        """
        widgetList = []
        for widget in self.widgetList:
                if widget.getOption(optionName) == optionValue:
                    widgetList.append(widget)
        return widgetList


    def getWidgetsByResource(self, pResource):
        """
        Recupere un ou des widgets selon une resource dans ses resources associees

        Args:
            pResource: La resource
        Returns:
            Liste de widget correspondant
        """
        widgetList = []
        for widget in self.widgetList:
            if hasattr(widget,'resources'):
                for resource in widget.resources:
                    if resource == pResource:
                        widgetList.append(widget)
            elif hasattr(widget,'resource'):
                if widget.resource == pResource:
                    widgetList.append(widget)
        return widgetList

    def getResourceWithDSWidget(self, dataOption):
        """
        Recupere une resource content un datastore avec l'option widgettype correspondante

        Args:
            dataOptions: l'option du datastore
        Returns
            Une resource
        """
        for resource in self.resourceList:
            for datastore in resource.datastores.all():
                try:
                    option = datastore.datastoreoption_set.filter(name="widgettype")
                    if option[0].value == dataOption:
                        return resource
                except IndexError:
                    pass


    def isInToolbar(self, widgetId):
        """
        Verifie si un widget dans une toolbar

        Args:
            widgetId: L'id du widget
        Returns:
            True or False
        """
        for widget in self.widgetList:
            if widget.type.name == "GeoExtToolbar":
                widgetItems = widget.getOption("widgets")
                for item in widgetItems:
                    if item == widgetId:
                        return True
                else:
                    return False


    def getServiceById(self, serviceId):
        """
        Recupere un service dans la base de donnee selon son id

        Args:
            idService: L'id du service
        Returns:
            Un service
        """
        try:
            service = Service.objects.get(id=serviceId)
            return service
        except Service.DoesNotExist:
            return False


