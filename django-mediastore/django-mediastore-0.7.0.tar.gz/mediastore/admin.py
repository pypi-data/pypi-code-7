# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.util import unquote
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from mediastore import media_url
from mediastore.fields import MediaField, MultipleMediaField
from mediastore.models import Media
from mediastore.preview import display_media
from mediastore.utils import get_media_models, get_model_for_type
from mediastore.utils.http import HttpJsonResponse
from mediastore.utils.models import order_queryset_by_pks
from mediastore.widgets import MediaTypeSelect


def admin_preview_media(*args, **kwargs):
    kwargs['template_name_single'] = 'admin/mediastore/media/object_preview.html'
    kwargs['template_name_many'] = 'admin/mediastore/media/many_object_preview.html'
    return display_media(*args, **kwargs)


class MediaTypeFilter(SimpleListFilter):
    title = _(u'Mediatype')
    parameter_name = 'content_type__model'

    def lookups(self, request, model_admin):
        types = []
        for model in get_media_models():
            types.append((
                model._meta.object_name.lower(),
                model._meta.verbose_name))
        return types

    def queryset(self, request, queryset):
        if 'content_type__model' in self.used_parameters:
            lookup = self.used_parameters['content_type__model']
            queryset = queryset.filter(content_type__model=lookup)
        return queryset



class SelectedFilter(SimpleListFilter):
    title = _(u'Selected')
    parameter_name = 'pk__in'

    def lookups(self, request, model_admin):
        return (
            ('', _('Selected')),
        )

    def queryset(self, request, queryset):
        if 'pk__in' in self.used_parameters:
            lookup = self.used_parameters['pk__in']
            lookup = [l for l in lookup.split(',') if l]
            queryset = queryset.filter(pk__in=lookup)
        return queryset


class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview', 'name', 'created')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    date_hierarchy = 'created'
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    actions_on_bottom = True

    def preview(self, obj):
        from mediastore.preview import preview_media
        return preview_media(obj, {'size':'100px'})
    preview.allow_tags = True

    MAIN_FIELDSET = (None, {
        'fields': ('name', 'description', 'slug', 'tags')
    })


class ModelAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if isinstance(db_field, MediaField):
            # prevent the + (add object) symbol from appearing
            self.raw_id_fields += (db_field.name,)
            return db_field.formfield(
                widget_kwargs={'admin_site': self.admin_site},
                **kwargs)
        return super(ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if isinstance(db_field, MultipleMediaField):
            # prevent the + (add object) symbol from appearing
            self.raw_id_fields += (db_field.name,)
            return db_field.formfield(
                widget_kwargs={'admin_site': self.admin_site},
                **kwargs)
        return super(ModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class MediaModelAdmin(admin.ModelAdmin):
    select_template = None

    list_display = ('slug', 'preview', 'name', 'content_type', 'created')
    list_display_links = ('slug', 'name')
    search_fields = ('name', 'description')
    date_hierarchy = 'created'
    list_filter = (MediaTypeFilter, SelectedFilter,)

    select_list_per_page = 25

    def preview(self, obj):
        from mediastore.preview import preview_media
        return preview_media(obj.object, {'size':'100px'})
    preview.allow_tags = True

    class add_form(forms.ModelForm):
        type = forms.CharField(
            label=_('Select the media type you want to add'),
            widget=MediaTypeSelect()
        )

        class Meta:
            model = Media
            fields = ('type',)
        class Media:
            js = (
                media_url('js/jquery-1.3.2.min.js'),
                media_url('js/mediatype_select.js'),
            )
            css = {
                'all': (media_url('css/mediatype_select.css'),)
            }

        def save(self, *args, **kwargs):
            raise NotImplementedError()
        def clean_type(self):
            self.cleaned_data['app_label'], \
            self.cleaned_data['model_name'] = \
                self.cleaned_data['type'].split('.', 1)
            return self.cleaned_data

    def add_view(self, request, *args, **kwargs):
        if request.GET.has_key('type'):
            model = get_model_for_type(request.GET['type'])
            url = urlresolvers.reverse(
                '%s:%s_%s_add' % (
                    self.admin_site.name,
                    model._meta.app_label.lower(),
                    model._meta.object_name.lower(),
                )
            )
            if request.REQUEST.has_key('_popup'):
                url += '?_popup=1'
            return HttpResponseRedirect(url)
        change_form = self.form
        try:
            self.form = self.add_form
            kwargs.setdefault('extra_context', {}).\
                setdefault('media_models', get_media_models())
            media_models = [
                model for model in get_media_models()
                if model in self.admin_site._registry
            ]
            field = self.form.base_fields['type']
            field_widget = field.widget
            field.widget = MediaTypeSelect(media_models=media_models)
            if request.method == 'POST':
                form = self.form(request.POST)
                if form.is_valid():
                    # TODO: continue work
                    admin_name = self.admin_site.name
                    # TODO: make url dynamic
                    url = urlresolvers.reverse(
                        '%s:%s_%s_add' % (
                            self.admin_site.name,
                            form.cleaned_data['app_label'],
                            form.cleaned_data['model_name'],
                        )
                    )
                    if request.REQUEST.get('_popup', None):
                        url += '?_popup=1'
                    return HttpResponseRedirect(url)
            response = super(MediaModelAdmin, self).\
                add_view(request, *args, **kwargs)
            field.widget = field_widget
            return response
        finally:
            self.form = change_form

    def change_view(self, request, object_id, extra_context=None):
        '''
        Redirects to the changeview of the correct model.
        '''
        # TODO(gregor@muellegger.de): find a way to automatically link back to
        # the media changelist after editing the specific model.
        try:
            media = self.queryset(request).get(pk=unquote(object_id))
            obj = media.object
            return HttpResponseRedirect(urlresolvers.reverse(
                '%s:%s_%s_change' % (
                    self.admin_site.name,
                    obj._meta.app_label,
                    obj._meta.object_name.lower(),
                ),
                args=(object_id,),
            ))
        except Media.DoesNotExist:
            response = super(MediaModelAdmin, self).\
                change_view(request, object_id, extra_context)
            return response

    def changelist_view(self, request, extra_context=None):
        if request.GET.get('pop', 0):
            return self.select_view(request, extra_context)
        return super(MediaModelAdmin, self).changelist_view(request, extra_context)

    def select_view(self, request, extra_context=None):
        if '_get_previews' in request.GET:
            try:
                pks = [int(pk) for pk in request.GET['_get_previews'].split(',')]
            except ValueError:
                pks = None
            if pks is not None:
                previews = []
                queryset = self.model._default_manager.filter(pk__in=pks)
                queryset = order_queryset_by_pks(queryset, pks)
                for obj in queryset:
                    previews.append({
                        'id': obj.pk,
                        'preview': admin_preview_media(obj),
                    })
                return HttpJsonResponse(previews)

        response = super(MediaModelAdmin, self).changelist_view(request, extra_context)
        if isinstance(response, TemplateResponse):
            opts = self.model._meta
            response.template_name = [
                'admin/%s/%s/select.html' % (opts.app_label, opts.object_name.lower()),
                'admin/%s/select.html' % opts.app_label,
                'admin/select.html'
            ]
        return response

    def select_many_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'multiple': True,
        })
        return self.select_view(request, extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url
        urlpatterns = super(MediaModelAdmin, self).get_urls()
        return patterns('',
            url(r'^select/$',
                self.admin_site.admin_view(self.select_view),
                name='mediastore_media_select'),
            url(r'^select-many/$',
                self.admin_site.admin_view(self.select_many_view),
                name='mediastore_media_select_many'),
        ) + urlpatterns

    def lookup_allowed(self, lookup, value):
        if lookup in ('content_type__model', 'content_type__model__in'):
            return True
        return super(MediaModelAdmin, self).lookup_allowed(lookup, value)


admin.site.register(Media, MediaModelAdmin)
