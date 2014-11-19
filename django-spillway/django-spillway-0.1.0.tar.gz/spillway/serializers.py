from django.contrib.gis.db import models
from rest_framework import serializers, pagination
from greenwich.srs import SpatialReference

from spillway.collections import Feature, FeatureCollection, NamedCRS
from spillway.fields import GeometryField, NDArrayField


class GeoModelSerializerOptions(serializers.ModelSerializerOptions):
    def __init__(self, meta):
        super(GeoModelSerializerOptions, self).__init__(meta)
        self.geom_field = getattr(meta, 'geom_field', None)


class GeoModelSerializer(serializers.ModelSerializer):
    """Serializer class for GeoModels."""
    _options_class = GeoModelSerializerOptions
    field_mapping = dict({
        models.GeometryField: GeometryField,
        models.PointField: GeometryField,
        models.LineStringField: GeometryField,
        models.PolygonField: GeometryField,
        models.MultiPointField: GeometryField,
        models.MultiLineStringField: GeometryField,
        models.MultiPolygonField: GeometryField,
        models.GeometryCollectionField: GeometryField
    }, **serializers.ModelSerializer.field_mapping)

    def get_default_fields(self):
        """Returns a fields dict for this serializer with a 'geometry' field
        added.
        """
        fields = super(GeoModelSerializer, self).get_default_fields()
        # Set the geometry field name when it's undeclared.
        if not self.opts.geom_field:
            for name, field in fields.items():
                if isinstance(field, GeometryField):
                    self.opts.geom_field = name
        return fields

class CRSField(serializers.Field):
    crscount = 0
    def to_native(self, value):
        #import ipdb; ipdb.set_trace()
        self.crscount += 1
        print 'COUNT:', self.crscount
        #return value
        return 4326

class FeatureSerializer(GeoModelSerializer):
    #crs = CRSField(source='*')
    def __init__(self, *args, **kwargs):
        super(FeatureSerializer, self).__init__(*args, **kwargs)
        self.fields[self.opts.geom_field].set_default_source()
        #try:
            ##self._crs = self.init_data['crs']
            #self.init_data = self.init_data['features']
        #except KeyError:
            #pass
        #view = self.context.get('view')
        #try:
            #wants_default_renderer = view.wants_default_renderer()
        #except AttributeError:
            #wants_default_renderer = True
        ## Alter the field source based on geometry output format.
        #if not wants_default_renderer:
            #renderer = view.request.accepted_renderer
            #self.fields[self.opts.geom_field].set_source(renderer.format)

    @property
    def data(self):
        if self._data is None:
            data = super(FeatureSerializer, self).data
            fieldname = self.opts.geom_field
            if self.many or isinstance(data, (list, tuple)):
                try:
                    srid = (self.object.query.transformed_srid or
                            self.object.geo_field.srid)
                except AttributeError:
                    srid = None
                self._data = FeatureCollection(features=data, crs=srid)
            else:
                try:
                    geom = getattr(self.object, fieldname)
                except AttributeError:
                    pass
                else:
                    self._data['crs'] = NamedCRS(geom.srid)
        return self._data

    #@property
    #def errors(self):

    def to_native(self, obj):
        native = super(FeatureSerializer, self).to_native(obj)
        geometry = native.pop(self.opts.geom_field)
        pk = native.pop(obj._meta.pk.name, None)
        return Feature(pk, geometry, native)

    # FIXME: How to handle many?
    def from_native(self, data, files=None):
        if data and 'features' in data:
            for feat in data['features']:
                return self.from_native(feat, files)
        try:
            sref = SpatialReference(data['crs']['properties']['name'])
        except KeyError:
            sref = None
        record = {self.opts.geom_field: data.get('geometry')}
        record.update(data.get('properties', {}))
        #FIXME: handle reprojection.
        feature = super(FeatureSerializer, self).from_native(record, files)
        if feature and sref:
            geom = getattr(feature, self.opts.geom_field)
            geom.srid = sref.srid
        return feature

class FeatureField(serializers.Field):
    def to_native(self, obj):
        native = super(FeatureField, self).to_native(obj)
        geometry = native.pop(self.opts.geom_field)
        pk = native.pop(obj._meta.pk.name, None)
        return Feature(pk, geometry, native)
class NFeatureSerializer(serializers.Serializer):
    def to_native(self, obj):
        native = super(NFeatureSerializer, self).to_native(obj)
        #geometry = native.pop(self.opts.geom_field)
        import ipdb; ipdb.set_trace()
        pk = native.pop(obj._meta.pk.name, None)
        return Feature(pk, geometry, native)

#FeatureCollectionSerializer({'features': GeoModel.objects.all()})
class FeatureCollectionSerializer(serializers.Serializer):
    #features = FeatureSerializer(many=True) # needs model set
    features = NFeatureSerializer(source='*')
    #features = FeatureField(source='*') # nested list
    #bbox = serializers.CharField()
    crs = CRSField(source='*')

    #def to_native(self, obj):
        #native = super(FeatureCollectionSerializer, self).to_native(obj)
        #import ipdb; ipdb.set_trace()
        #return native

class PaginatedFeatureSerializer(pagination.PaginationSerializer):
    results_field = 'features'


class RasterModelSerializerOptions(GeoModelSerializerOptions):
    def __init__(self, meta):
        super(RasterModelSerializerOptions, self).__init__(meta)
        self.raster_field = getattr(meta, 'raster_field', None)


class RasterModelSerializer(GeoModelSerializer):
    _options_class = RasterModelSerializerOptions

    #def __init__(self, *args, **kwargs):
        #rformat = kwargs.pop('format', None)
        #super(RasterModelSerializer, self).__init__(*args, **kwargs)
        #if not rformat:
            #request = self.context.get('request')
            #if request:
                #rformat = request.accepted_renderer.format
        #self.format = rformat
        ##self.fields['image'].format = rformat

    def get_default_fields(self):
        fields = super(RasterModelSerializer, self).get_default_fields()
        if not self.opts.raster_field:
            for name, field in fields.items():
                if isinstance(field, serializers.FileField):
                    self.opts.raster_field = name
        request = self.context.get('request')
        render_format = request.accepted_renderer.format if request else None
        # Serialize image data as arrays when json is requested.
        if render_format == 'json':
            fields[self.opts.raster_field] = NDArrayField()
        elif render_format in ('api', 'html'):
            pass
        elif self.opts.raster_field and 'path' not in fields:
            # Add a filepath field for GDAL based renderers.
            fields['path'] = serializers.CharField(
                source='%s.path' % self.opts.raster_field)
        return fields

    #def to_native(self, obj):
        #params = self.context.get('params', {})
        #geom = params.get('g')
        ##request = self.context.get('request')
        ##format = request and request.accepted_renderer.format
        #if callable(getattr(obj, 'clip', None)):
            #clip = obj.clip(geom, self.format)
            ##import ipdb; ipdb.set_trace()
            #if clip:
                #setattr(obj, self.opts.raster_field, clip)
        #return super(RasterModelSerializer, self).to_native(obj)


class RasterCatalogSerializer(serializers.HyperlinkedModelSerializer):
    pass


#class RasterStoreSerializer(serializers.HyperlinkedModelSerializer):
    ##tile_url = serializers.URLField(read_only=True)
    ##source = serializers.URLField(source='gdal.url', read_only=True)
    #path = serializers.CharField(source='gdal.path', read_only=True)
    ##source = serializers.ImageField()
    ##source = serializers.FileField()

    #class Meta:
        ##model = RasterStore
        #exclude = ('gdal', 'proj4')


#{'map': 'map.xml', 'style': 'default', 'layer': obj.layer, 'srs': 'epsg:3857'}
class MapnikSerializer(serializers.Serializer):
    mapfile = serializers.CharField(required=False)
    bbox = GeometryField(required=False)
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    z = serializers.IntegerField()
    #band = serializers.IntegerField(default=1)
    style = serializers.CharField(required=False)
    #srs =

    def to_native(self, obj):
        obj = super(MapnikSerializer, self).to_native(obj)
        nikmap = mapnik.Map(256, 256)
        nikmap.buffer_size = 128
        mapnik.load_map(nikmap, mapfile)
        layer = obj.layer()
        x, y, z = map(obj.get, ('x', 'y', 'z'))
        obj['bbox'] = transform_tile(x, y, z) + transform_tile(x + 1, y + 1, z)
        style = nikmap.find_style('default')
        rule = style.rules[0]
        symbolizer = rule.symbols[0]
        # Generate equal interval bins from min/max pixel values.
        breaks = np.linspace(self.object.minval, self.object.maxval,
                             len(symbolizer.colorizer.stops))
        # Update the stop values for the color ramp.
        for stop, breakval in zip(symbolizer.colorizer.stops, breaks):
            stop.value = breakval
        #layer.styles.append(style.name)
        layer.styles.append('default')
        # Must append layer to map *after* appending style to it.
        nikmap.layers.append(layer)
        bbox.transform(nikmap.srs)
        nikmap.zoom_to_box(mapnik.Box2d(*bbox.extent))
        img = mapnik.Image(nikmap.width, nikmap.height)
        mapnik.render(nikmap, img)
        return img.tostring('png')

    #def from_native(self, obj, files=None):
        #print 'OBJECT', obj
    #def restore_object(self, attrs, instance=None):
        #nikmap = mapnik.Map(256, 256)
        #nikmap.buffer_size = 128
        #mapnik.load_map(nikmap, mapfile)
        #return nikmap
