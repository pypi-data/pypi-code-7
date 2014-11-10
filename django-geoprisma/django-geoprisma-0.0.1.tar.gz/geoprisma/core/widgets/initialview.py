import requests
from widgetbase import WidgetBase


class InitialView(WidgetBase):
    """
    InitialView
    """

    def getLocalViewIndex(self, request):
        """
        Recupere la valeur du localViewField dans les options ou dans la requete

        Args:
            request: L'object request
        Returns:
            L'index du local view
        """
        if self.getOption("localViewField"):
                return self.getOption("localViewField")
        else:
            if request.GET:
                try:
                    return request.GET['localViewField']
                except KeyError:
                    return 0

    def getlocalViewString(self, index):
        """
        Recupere la valeur de l'option localview selon une index

        Args:
            index: L'index
        Returns:
            La valeur de l'option localview
        """
        if index > 1:
            pass
        elif index == 1:
            if self.getOption("localView"):
                return self.getOption("localView")
        else:
            return False

    def getFeature(self, datastore, viewId):
        if datastore and viewId != "":
            url = datastore.service.source + "/" + str(datastore.layers) + "/" + viewId + ".geojson"
            requestUrl = requests.get(url)
            return requestUrl.text
        else:
            return False

