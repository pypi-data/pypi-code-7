from collective.geo.mapwidget.maplayers import MapLayer
from plone.memoize.instance import memoizedproperty


class SourceLayer(MapLayer):
    """ A custom layer for placemap sources that extends the default with
    additional properties that are added to the javascript code.

    """

    js_template = u"""
        function() {
            return seantis.placemap.create_kml_layer(
                '%(url)s', '%(title)s', '%(color)s'
            );
        }
    """

    @memoizedproperty
    def jsfactory(self):
        return self.js_template % dict(
            url=self.url, title=self.title, color=self.color
        )

    @staticmethod
    def from_source(source):
        layer = SourceLayer()

        layer.id = source.id
        layer.title = source.Title.decode('utf-8')
        layer.url = source.getURL() + '/kml-document'
        layer.color = source.color

        return layer
