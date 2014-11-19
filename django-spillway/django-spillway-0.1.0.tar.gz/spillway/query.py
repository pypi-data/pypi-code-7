from django.contrib.gis import geos
from django.contrib.gis.db.models import query
from django.db import connection

# Many GeoQuerySet methods cannot be chained as expected and extending
# GeoQuerySet to work properly with serialization calls like
# .simplify(100).svg() will require patching
# django.contrib.gis.db.models.query. Work around this with a custom
# GeoQuerySet for now.
class GeoQuerySet(query.GeoQuerySet):
    """Extends the default GeoQuerySet with some unimplemented PostGIS
    functionality.
    """
    _scale = '%s(%%s, %%s, %%s)' % connection.ops.scale
    # Geometry outputs
    _formats = {'geojson': '%s(%%s, %%s)' % connection.ops.geojson,
                #'json': '%s(%%s, %%s)' % connection.ops.geojson,
                'kml': '%s(%%s, %%s)' % connection.ops.kml,
                'svg': '%s(%%s, 0, %%s)' % connection.ops.svg}
    # Json is an alias for geojson.
    #_formats['json'] = _formats['geojson']

    def _as_format(self, sql, format=None, precision=6):
        val = self._formats.get(format, self._formats['geojson'])
        return self.extra(select={format: val % (sql, precision)})

    def _transform(self, colname, srid=None):
        # FIXME: Used for different purposes?!
        #self.query.transformed_srid = srid
        # Transform for the side effect of changing geom srid.
        if srid:
            self.transform(srid)
        return ('%s(%s, %s)' % (connection.ops.transform, colname, srid)
                if srid else colname)

    def _simplify(self, colname, tolerance=0.0):
        # connection.ops does not have simplify available for PostGIS.
        return ('ST_Simplify(%s, %s)' % (colname, tolerance)
                if tolerance else colname)

    def extent(self, srid=None):
        """Returns the GeoQuerySet extent as a 4-tuple.

        The method chaining approach of
        geoqset.objects.transform(srid).extent() returns the extent in the
        original coordinate system, this method allows for transformation.

        Keyword args:
        srid -- EPSG id for for transforming the output geometry.
        """
        if not srid and not connection.ops.spatialite:
            return super(GeoQuerySet, self).extent()
        transform = self._transform(self.geo_field.column, srid)
        # Spatialite extent() is supported post-1.7.
        if connection.ops.spatialite:
            ext = {'extent': 'AsText(%s(%s))' % ('Extent', transform)}
        else:
            ext = {'extent': '%s(%s)' % (connection.ops.extent, transform)}
        try:
            # The bare order_by() is needed to remove the default sort field
            # which is not present in this aggregation.
            extent = (self.extra(select=ext)
                          .values_list('extent', flat=True)
                          .order_by()[0])
        except IndexError:
            return ()
        try:
            return connection.ops.convert_extent(extent)
        except NotImplementedError:
            return geos.GEOSGeometry(extent, srid).extent

    def filter_geometry(self, **kwargs):
        """Convenience method for providing spatial lookup types as keywords
        without underscores instead of the usual "geometryfield__lookuptype"
        format.
        """
        fieldname = self.geo_field.name
        query = {'%s__%s' % (fieldname, key): val
                 for key, val in kwargs.items()}
        return self.filter(**query)

    @property
    def geo_field(self):
        return self.query._geo_field()

    def scale(self, x, y, z=0.0, tolerance=0.0, precision=6, srid=None,
              format=None, **kwargs):
        """Returns a GeoQuerySet with scaled and optionally reprojected and
        simplified geometries, serialized to a supported format.
        """
        if not any((tolerance, srid, format)):
            return super(GeoQuerySet, self).scale(x, y, z, **kwargs)
        transform = self._transform(self.geo_field.column, srid)
        scale = self._scale % (transform, x, y)
        simplify = self._simplify(scale, tolerance)
        return self._as_format(simplify, format, precision)

    def simplify(self, tolerance=0.0, srid=None, format=None, precision=6):
        """Returns a GeoQuerySet with simplified geometries serialized to
        a supported geometry format.
        """
        # Transform first, then simplify.
        transform = self._transform(self.geo_field.column, srid)
        if format:
            simplify = (self._simplify(transform, tolerance)
                        if tolerance else transform)
            return self._as_format(simplify, format, precision)
        simplify = self._simplify(transform, tolerance)
        #FIXME: Should be "name" not "column" right?
        # TODO: EWKB bug is fixed in spatialite 4.2+ so this can be removed.
        if connection.ops.spatialite:
            simplify = 'AsEWKT(%s)' % simplify
        return self.extra(select={self.geo_field.column: simplify})


        # Simplify, then transform.
        simplify = self._simplify(self.geo_field.column, tolerance)
        transform = self._transform(simplify, srid) if srid else simplify
        if format:
            return self._as_format(transform, format, precision)
        #FIXME: Should be "name" not "column" right?
        return self.extra(select={self.geo_field.column: self._wkb(transform)})

    # FIXME: add preserve_topology
    def nosimplify(self, tolerance=0.0, srid=None, format=None, precision=6):
        #'self.query.extra': {'intersection': (u'ST_Intersection("coredata_ecoregion"."the_geom",%s)',
        #import ipdb; ipdb.set_trace()
        try:
            attr, query = self.query.extra.popitem()
        except KeyError:
            #simplify = self._simplify(self.geo_field.column, tolerance)
            attr = self.geo_field.name
            query = (self.geo_field.column, '') # need the postgis adapter object.

        simplify = self._simplify(query[0], tolerance)
        transform = self._transform(simplify, srid) if srid else simplify
        if format:
            val = self._formats.get(format, self._formats['geojson'])
            geoformat = val % (transform, precision)
            self.query.extra[format] = (geoformat, query[1])
            #return self
            return self._clone()
        #return self.extra(select={self.geo_field.column: self._wkb(transform)})
        self.query.extra[attr] = (self._wkb(transform), query[1])
        #return self
        return self._clone()

    #def _merge_extra(self, vals):
        #self.query.extra

    #def tile(self, tilecoord):

    def _no_transform(self, srid=4326, **kwargs):
        """
        Transforms the given geometry field to the given SRID.  If no SRID is
        provided, the transformation will default to using 4326 (WGS84).
        """
        import ipdb; ipdb.set_trace()
        #if not isinstance(srid, six.integer_types):
            #raise TypeError('An integer SRID must be provided.')
        field_name = kwargs.get('field_name', None)
        tmp, geo_field = self._spatial_setup('transform', field_name=field_name)

        # Getting the selection SQL for the given geographic field.
        field_col = self._geocol_select(geo_field, field_name)

        # Why cascading substitutions? Because spatial backends like
        # Oracle and MySQL already require a function call to convert to text, thus
        # when there's also a transformation we need to cascade the substitutions.
        # For example, 'SDO_UTIL.TO_WKTGEOMETRY(SDO_CS.TRANSFORM( ... )'
        geo_col = self.query.custom_select.get(geo_field, field_col)

        # Setting the key for the field's column with the custom SELECT SQL to
        # override the geometry column returned from the database.
        custom_sel = '%s(%s, %s)' % (connection.ops.transform, geo_col, srid)
        # TODO: Should we have this as an alias?
        # custom_sel = '(%s(%s, %s)) AS %s' % (SpatialBackend.transform, geo_col, srid, qn(geo_field.name))
        self.query.transformed_srid = srid # So other GeoQuerySet methods
        self.query.custom_select[geo_field] = custom_sel
        return self._clone()

    #def _spatial_attribute(self, att, settings, field_name=None, model_att=None):
    def __spatial_attribute(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        extra = super(GeoQuerySet, self)._spatial_attribute(*args, **kwargs)
        return extra
