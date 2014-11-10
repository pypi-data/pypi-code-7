import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.admin import helpers
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.gis.admin import GeoModelAdmin
from modeltranslation.admin import TranslationAdmin
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.contrib.admin.util import quote
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.http import Http404, HttpResponseRedirect
from django.utils.html import escape
from django import forms, template


import copy
from django.core.exceptions import ObjectDoesNotExist


from .models import *
from .forms import *
from .utils import join_url

try:
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns

# Si le parametre 'parenthesis' est a True, le nombre est rajoute entre parenthese (X)
# Sinon, il est rajoute apres un tiret -X

def get_duplicate_name_field(model, field, initial_value, parenthesis=True):
    resource_name_init = initial_value
    resource_name_duplicate = ''
    boucleNumCopie = True
    numCopie = 1

    while boucleNumCopie:
        try:
            if parenthesis:
                resource_name_duplicate = resource_name_init + '(' + str(numCopie) + ')'
            else:
                resource_name_duplicate = resource_name_init + '-' + str(numCopie)

            args = {field:resource_name_duplicate}
            model.objects.get(**args)
            numCopie += 1
        except ObjectDoesNotExist:
            boucleNumCopie = False

    return resource_name_duplicate;

# Actions
def dupliquer_les_resources(modeladmin, request, queryset):
    for resource in queryset:
        # django copy object
        resource_copy = copy.copy(resource)
        # set 'id' to None to create new object
        resource_copy.pk = None

        #Get duplicate name for name and slug
        resource_copy.name = get_duplicate_name_field(Resource, 'name', resource_copy.name)
        resource_copy.slug = get_duplicate_name_field(Resource, 'slug', resource_copy.slug, False)

        # initial save
        resource_copy.save()

        # copy M2M relationship: 'datastores', 'accessfilters', 'fields', 'ResourceOption'
        for datastore in resource.datastores.all():
               resource_copy.datastores.add(datastore)
        resource_copy.save()

        for accessfilter in resource.accessfilters.all():
               ra = ResourceAccessfilter(resource=resource_copy,
                                         accessfilter=accessfilter)
               ra.save()

        for ressfield in ResourceField.objects.filter(resource=resource):
               rf = ResourceField(resource=resource_copy,
                                  field=ressfield.field,
                                  order=ressfield.order)
               rf.save()

        for ress_opt in ResourceOption.objects.filter(resource=resource):
               ro = ResourceOption(resource=resource_copy,
                             name=ress_opt.name,
                             value=ress_opt.value,
                             key=ress_opt.key,
                             domain=ress_opt.domain)
               ro.save()


def dupliquer_les_mapcontext(modeladmin, request, queryset):
    for mapcontext in queryset:
        # django copy object
        mapcontext_copy = copy.copy(mapcontext)
        # set 'id' to None to create new object
        mapcontext_copy.pk = None

        #Get duplicate name for name
        mapcontext_copy.name = get_duplicate_name_field(MapContext, 'name', mapcontext_copy.name)

        # initial save
        mapcontext_copy.save()

        # copy M2M relationship: 'MapContextOption', 'MapContextResource'
        for mapc_opt in MapContextOption.objects.filter(mapContext=mapcontext):
               mo = MapContextOption(mapContext=mapcontext_copy,
                                     name=mapc_opt.name,
                                     value=mapc_opt.value)
               mo.save()

        for mapc_ress in MapContextResource.objects.filter(mapContext=mapcontext):
               mr = MapContextResource(mapContext=mapcontext_copy,
                                        resource=mapc_ress.resource,
                                        order=mapc_ress.order)
               mr.save()


def dupliquer_les_datastores(modeladmin, request, queryset):
    for datastore in queryset:
        # django copy object
        datastore_copy = copy.copy(datastore)
        # set 'id' to None to create new object
        datastore_copy.pk = None

        #Get duplicate name for name
        datastore_copy.name = get_duplicate_name_field(Datastore, 'name', datastore_copy.name)

        # initial save
        datastore_copy.save()

        # copy M2M relationship: 'DatastoreOption'
        for d_opt in DatastoreOption.objects.filter(datastore=datastore):
               do = DatastoreOption(datastore=datastore_copy,
                                     name=d_opt.name,
                                     value=d_opt.value)
               do.save()



def dupliquer_les_applications(modeladmin, request, queryset):
    for application in queryset:
        # django copy object
        application_copy = copy.copy(application)
        # set 'id' to None to create new object
        application_copy.pk = None

        #Get duplicate name for name
        application_copy.name = get_duplicate_name_field(Application, 'name', application_copy.name)

        # initial save
        application_copy.save()

        # copy M2M relationship: 'ApplicationWidget'
        for a_wid in ApplicationWidget.objects.filter(application=application):
               aw = ApplicationWidget(application=application_copy,
                                     widget=a_wid.widget,
                                     order=a_wid.order)
               aw.save()

# Inlines
class DefaultLayerOptionInline(admin.TabularInline):
    form = DefaultLayerOptionForm
    model = DefaultLayerOption
    extra = 2


class ServiceOptionInline(admin.TabularInline):
    form = ServiceOptionForm
    model = ServiceOption
    extra = 2


class DatastoreOptionInline(admin.TabularInline):
    form = DatastoreOptionForm
    model = DatastoreOption
    extra = 2


class ResourceFieldInline(admin.TabularInline):
    model = ResourceField
    extra = 5


class ResourceOptionInline(admin.TabularInline):
    form = ResourceOptionForm
    model = ResourceOption
    extra = 5


class FieldOptionInline(admin.TabularInline):
    form = FieldOptionForm
    model = FieldOption
    extra = 5


class AccessFilterOptionInline(admin.TabularInline):
    form = AccessFilterOptionForm
    model = AccessFilterOption
    extra = 5


class WidgetOptionInline(admin.TabularInline):
    form = WidgetOptionForm
    model = WidgetOption
    extra = 5


class MapContextOptionInline(admin.TabularInline):
    form = MapContextOptionForm
    model = MapContextOption
    extra = 5


class MapContextResourceInline(admin.TabularInline):
    model = MapContextResource
    extra = 5


class ApplicationWidgetInline(admin.TabularInline):
    model = ApplicationWidget
    extra = 5


class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'activated')
    search_fields = ('name',)
    inlines = (DefaultLayerOptionInline,)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (ServiceOptionInline,)


class DatastoreAdmin(admin.ModelAdmin):
    form = DatastoreForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (DatastoreOptionInline,)
    actions = [dupliquer_les_datastores]


class ResourceAdmin(TranslationAdmin):
    list_display = ('pk', 'name',)
    search_fields = ('name',)
    inlines = (ResourceOptionInline, ResourceFieldInline)
    filter_horizontal = ('datastores', 'accessfilters', )
    actions = [dupliquer_les_resources]



class FieldAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (FieldOptionInline,)


class AccessFilterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (AccessFilterOptionInline,)


class WidgetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'activated')
    search_fields = ('name',)


class WidgetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (WidgetOptionInline,)



class MapContextAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (MapContextOptionInline, MapContextResourceInline)
    actions = [dupliquer_les_mapcontext]



class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'activated')
    search_fields = ('name',)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (ApplicationWidgetInline,)
    actions = [dupliquer_les_applications]



class SessionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    pass  # do not remove this class

class InitialViewAdmin(GeoModelAdmin):
    ordering = ['name', ]
    search_fields = ['name', 'description']
    list_display = ('name', 'description', 'id_session',)
    list_filter = ('id_session',)

    map_srid = 32187
    form = GeoForm

admin.site.register(Datastore, DatastoreAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(AccessFilter, AccessFilterAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(WidgetType, WidgetTypeAdmin)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(MapContext, MapContextAdmin)
admin.site.register(ApplicationType, ApplicationTypeAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(InitialView, InitialViewAdmin)
