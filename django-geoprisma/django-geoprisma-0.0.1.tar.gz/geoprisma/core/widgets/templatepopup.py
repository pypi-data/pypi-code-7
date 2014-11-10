from widgetbase import WidgetBase


class TemplatePopup(WidgetBase):

    def getServiceType(self):
        return "wfs"
    
    def needLayer(self):
        return True