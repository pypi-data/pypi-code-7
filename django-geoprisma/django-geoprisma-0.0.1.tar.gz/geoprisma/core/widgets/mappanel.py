from widgetbase import WidgetBase
from geoprisma.models import WidgetType

class MapPanel(WidgetBase):
    """
    MapPanel
    """
    def __init__(self, widgetModel):
        self.id = widgetModel.name
        self.name = widgetModel.name
        self.type = WidgetType(name="mappanel")
        self.action = "read"
        self.options = self.setOptions(widgetModel.mapcontextoption_set.all())
        
