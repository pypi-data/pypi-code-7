from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as geomodels
from django.template.defaultfilters import slugify



#Dummy decorator if schema is not supported
def schematize(original_class):
        return original_class

#Import model that support PGSQL schema if difined
if hasattr(settings,'SCHEMATIZED_MODELS'):
        try:
                models = __import__(settings.SCHEMATIZED_MODELS, fromlist=['*'])
                schematize = models.schematize
        except ImportError:
                from django.db import models
else:
        from django.db import models


@schematize
class ServiceType(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    activated = models.BooleanField(default=True)
    priority = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class DefaultLayerOption(models.Model):
    servicetype = models.ForeignKey(ServiceType)
    name = models.CharField(max_length=255)
    value = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class ServiceManager(models.Manager):
    def getService(self, slug):
        return self.model.objects.get(slug=slug)

@schematize
class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    objects = ServiceManager()
    type = models.ForeignKey(ServiceType)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Service, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("service", (), {"slug": self.slug})


@schematize
class ServiceOption(models.Model):
    service = models.ForeignKey(Service)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

@schematize
class Datastore(models.Model):
    service = models.ForeignKey(Service)
    name = models.CharField(max_length=255, unique=True)
    layers = models.CharField(max_length=255,null=True)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class DatastoreOption(models.Model):
    datastore = models.ForeignKey(Datastore)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class Field(models.Model):
    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    key = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class FieldOption(models.Model):
    field = models.ForeignKey(Field)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class AccessFilter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    commentaire = models.TextField(null=True, blank=True)


    def __unicode__(self):
        return self.name


@schematize
class AccessFilterOption(models.Model):
    accessfilter = models.ForeignKey(AccessFilter)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)


    def __unicode__(self):
        return self.name


class ResourceManager(models.Manager):
    def getResource(self, slug):
        return self.model.objects.get(slug__iexact=slug)


@schematize
class Resource(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acl_name = models.CharField(max_length=255,null=True, blank=True, db_column='acl_name')
    key = models.CharField(max_length=255,null=True, blank=True)
    domain = models.CharField(max_length=255,null=True, blank=True)
    datastores = models.ManyToManyField(Datastore, db_table= 'geoprisma_resourcedatastore')
    accessfilters = models.ManyToManyField(AccessFilter, null=True, blank=True, through='ResourceAccessfilter')
    fields = models.ManyToManyField(Field, through='ResourceField')
    slug = models.SlugField(max_length=255, unique=True, null=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    objects = ResourceManager()
    commentaire = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Resource, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("resource", (), {"slug": self.slug})


@schematize
class ResourceField(models.Model):
    resource = models.ForeignKey(Resource)
    field = models.ForeignKey(Field)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(resource=self.resource).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1

        return super(ResourceField, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.field.name

@schematize
class ResourceAccessfilter(models.Model):
    resource = models.ForeignKey(Resource)
    accessfilter = models.ForeignKey(AccessFilter)

    def __unicode__(self):
        return self.accessfilter.name

@schematize
class ResourceOption(models.Model):
    resource = models.ForeignKey(Resource)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)
    key = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class WidgetType(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    activated = models.BooleanField(default=True)
    classname = models.CharField(max_length=255, default='geoprisma.core.widgets.widgetbase.WidgetBase')
    action = models.CharField(max_length=255, default='read')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class Widget(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey(WidgetType)
    commentaire = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class WidgetOption(models.Model):
    widget = models.ForeignKey(Widget)
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(widget=self.widget).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1

        return super(WidgetOption, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


@schematize
class MapContext(models.Model):
    name = models.CharField(max_length=255, unique=True)
    resources = models.ManyToManyField(Resource, through='MapContextResource')
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class MapContextOption(models.Model):
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')
    name = models.CharField(max_length=255)
    value = models.TextField( null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class MapContextResource(models.Model):
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')
    resource = models.ForeignKey(Resource)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(mapContext=self.mapContext).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1

        return super(MapContextResource, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.resource.name


@schematize
class ApplicationType(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    activated = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class Application(models.Model):
    name = models.CharField(max_length=255, unique=True)
    template = models.CharField(max_length=255, default="")
    type = models.ForeignKey(ApplicationType)
    widgets = models.ManyToManyField(Widget, through='ApplicationWidget')
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@schematize
class ApplicationWidget(models.Model):
    application = models.ForeignKey(Application)
    widget = models.ForeignKey(Widget)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(application=self.application).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1

        return super(ApplicationWidget, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.widget.name


@schematize
class Session(models.Model):
    name = models.CharField(max_length=255, unique=True)
    application = models.ForeignKey(Application)
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

@schematize
class InitialView(models.Model):
    id_initial_view = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    id_session = models.ForeignKey(Session)
    geom = geomodels.GeometryField(srid=32187)
    sort_index = models.IntegerField()

    def __unicode__(self):
        return self.name + ' (' + self.id_session.name + ')'
