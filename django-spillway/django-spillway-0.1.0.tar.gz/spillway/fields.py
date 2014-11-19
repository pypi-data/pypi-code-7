"""Serializer fields"""
from django.contrib.gis import forms
from rest_framework.fields import FileField, WritableField
from greenwich import io, Raster

from spillway.compat import json


class GeometryField(WritableField):
    type_name = 'GeometryField'
    type_label = 'geometry'
    form_field_class = forms.GeometryField
    # TODO: Introspect available formats from spatial backends.
    _formats = ('geohash', 'geojson', 'gml', 'kml', 'svg')
    #_formats = ('geohash', 'geojson', 'gml', 'json', 'kml', 'svg')

    def set_default_source(self):
        """Set a default source based on the selected renderer."""
        # Do not override an explicitly provided field source.
        if self.source:
            return
        view = self.context.get('view')
        # Alter the field source based on geometry output format.
        try:
            wants_default_renderer = view.wants_default_renderer()
        except AttributeError:
            wants_default_renderer = True
        # Alter the field source based on geometry output format.
        if not wants_default_renderer:
            renderer = view.request.accepted_renderer
            if renderer.format in self._formats:
                self.source = renderer.format
                # Single objects must use GEOSGeometry attrs to provide formats.
                if not self.parent.many:
                    self.source = '%s.%s' % (self.label, self.source)

    #def set_format(self, format):
    #def set_source(self, format):
    def use_format(self, format):
        if self.source:
            return
        if format in self._formats:
            self.source = format
            # Single objects must use GEOSGeometry attrs to provide formats.
            if not self.parent.many:
                self.source = '%s.%s' % (self.label, self.source)

    def to_native(self, value):
        # Create a dict from the GEOSGeometry when the value is not previously
        # serialized from the spatial db.
        try:
            return {'type': value.geom_type, 'coordinates': value.coords}
        # Value is already serialized as geojson, kml, etc.
        except AttributeError:
            return value

    def from_native(self, value):
        # forms.GeometryField cannot handle geojson dicts.
        if isinstance(value, dict):
            value = json.dumps(value)
        return super(GeometryField, self).from_native(value)


class NDArrayField(FileField):
    type_name = 'NDArrayField'
    type_label = 'ndarray'

    def to_native(self, value):
        params = self.context.get('params', {})
        geom = params.get('g')
        #band = params.get('band')
        with Raster(getattr(value, 'path', value)) as r:
            #if band:
                #rband = r[band]
            #arr = r.clip(geom).masked_array() if geom else r.array()
            arr = r.clip(geom).array() if geom else r.array()
            if not geom:
                return r.array().tolist()
            with r.clip(geom) as clipped:
                return clipped.array().tolist()
        #r = Raster(getattr(value, 'path', value))
        #arr = r.clip(geom).masked_array() if geom else r.array()
        #arr = r.clip(geom).array() if geom else r.array()
        #r.close()
        #func = params.get('filter_func')
        # FIXME: Handle ints, float32 has rounding issues, why do we have to
        # cast to float64?
        #return (func(arr) if func else arr).astype(float).round(4).tolist()
        #return arr.tolist()


class GDALField(FileField):
    type_name = 'GDALField'
    type_label = 'gdaldataset'

    #def initialize(self, *args, **kwargs):
        #super(GDALField, self).initialize(*args, **kwargs)

    #def to_native(self, value):
        #return value.path

    def not_to_native(self, value):
        print 'VALUE', type(value), value
        #if value is None: #FIXME: field_to_native should not call this with None?
            #raise Exception
        params = self.context.get('params', {})
        geom = params.get('g')
        request = self.context.get('request')
        format = request and request.accepted_renderer.format or getattr(self, 'format', None)
        #if not request:
        if not format:
            return value.path
        #format = request.accepted_renderer.format
        assert '.' in format
        # No conversion is needed if the original format without clipping
        # is requested.
        if not geom and value.name.endswith(format):
            return value.path
        memio = io.MemFileIO(suffix=format)
        with Raster(value.path) as r:
            if geom:
                with r.clip(geom) as clipped:
                    clipped.save(memio)
            else:
                r.save(memio)
        imgdata = memio.read()
        memio.close()
        return imgdata
