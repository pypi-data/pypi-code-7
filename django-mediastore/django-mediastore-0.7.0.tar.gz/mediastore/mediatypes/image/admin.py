# -*- coding: utf-8 -*-
import os
import stat
import shutil
import zipfile
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import template
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from functools import update_wrapper
from taggit.forms import TagField
from mediastore.admin import MediaAdmin
from mediastore.conf import settings
from mediastore.mediatypes.image.models import Image

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class BatchUploadForm(forms.Form):
    archive = forms.FileField(label=_('Zip archive with images'))
    name_scheme = forms.CharField(
        label=_('Naming scheme'),
        help_text=_(
            'Naming scheme for batch renaming. It must contain '
            '(but only once) the "#" sign which is replaced by '
            'a continous number. If it is empty, the original filename '
            'will be taken as name.'
        ),
        max_length=250,
        required=False
    )
    tags = TagField(
        label=_('Tags'), required=False,
        help_text=_(
            'Specify a set of tags that are assigned to all new generated '
            'images.')
    )

    def clean_archive(self):
        zip1 = StringIO()
        for line in self.cleaned_data['archive'].chunks():
            zip1.write(line)
        try:
            zip2 = zipfile.ZipFile(zip1)
        except zipfile.BadZipfile:
            raise forms.ValidationError(_('Please supply a valid zipfile.'))
        if zip2.testzip() is not None:
            raise forms.ValidationError(_('Please supply a valid zipfile.'))
        return zip2

    def clean_name_scheme(self):
        if self.data['name_scheme'] == '':
            return ''
        elif self.data['name_scheme'].count('#') != 1:
            raise forms.ValidationError, _(
                'Name scheme must either contain one "#" sign or must be '
                'empty.')
        else:
            return self.data['name_scheme']

    def get_namelist(self):
        archive = self.cleaned_data['archive']
        return archive.namelist()

    def get_file(self, filename):
        archive = self.cleaned_data['archive']
        return archive.read(filename)

    def apply_name_scheme(self, filename, count):
        name_scheme = self.cleaned_data['name_scheme']
        if not name_scheme:
            return filename
        return name_scheme.replace('#', force_unicode(count))

    def extract_to_file(self, filename, destdir):
        try:
            from PIL import Image
        except ImportError:
            import Image

        archive = self.cleaned_data['archive']
        data = archive.read(filename)
        file_data = StringIO(data)
        try:
            Image.open(file_data)
        except:
            return False
        outfile = os.path.join(destdir, filename.replace('/', '__'))
        # check if file would overwrite existing one
        while os.path.exists(outfile):
            name, ext = os.path.splitext(outfile)
            outfile = '%s_%s' % (name, ext)
        dirname = os.path.dirname(outfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname, 0775)
        photofile = file(outfile, 'wb')
        photofile.write(file_data.getvalue())
        photofile.close()
        if outfile.startswith(settings.MEDIA_ROOT):
            outfile = outfile[len(settings.MEDIA_ROOT):]
            if outfile.startswith('/'):
                outfile = outfile[1:]
        return outfile

    def save(self, model_class):
        destdir = os.path.join(
            settings.MEDIA_ROOT,
            settings.MEDIASTORE_FS_PREFIX,
            'images',
        )
        object_list = []
        count = 1
        for filename in self.get_namelist():
            name = self.apply_name_scheme(filename, count)
            imagefile = self.extract_to_file(filename, destdir)
            if imagefile:
                obj = model_class(
                    name=name,
                    file=imagefile,
                )
                obj.save()
                obj.tags.set(*self.cleaned_data['tags'])
                count += 1
                object_list.append(obj)
        return object_list


class ImageAdmin(MediaAdmin):
    list_display = (
        'id',
        'preview',
        'name',
        'width',
        'height',
        'mimetype',
        'created')
    list_filter = ('mimetype',)

    add_many_form = BatchUploadForm
    add_many_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'archive',
                'name_scheme',
                'tags',
            ),
        }),
    )

    def render_add_many_form(self, request, context, form_url=''):
        opts = self.model._meta
        app_label = opts.app_label
        add = add_many = True
        change = False
        context.update({
            'add': add,
            'add_many': add_many,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': False,
            'save_on_top': False,
        })
        context_instance = template.RequestContext(request,
            current_app=self.admin_site.name)
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/add_many_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/add_many_form.html" % app_label,
            "admin/add_many_form.html"
        ], context, context_instance=context_instance)

    def add_many_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.add_many_form
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                object_list = form.save(model)
                self.message_user(request, _(
                    '%(count)d %(verbose_name_plural)s were added successfully.') % {
                        'count': len(object_list),
                        'verbose_name_plural': force_unicode(
                            opts.verbose_name_plural)})
                if self.has_change_permission(request, None):
                    post_url = '../'
                else:
                    post_url = '../../../'
                return HttpResponseRedirect(post_url)
        else:
            form = ModelForm()

        adminForm = helpers.AdminForm(form, self.add_many_fieldsets, {})
        media = self.media + adminForm.media

        inline_admin_formsets = []

        context = {
            'title': _('Add multiple %s') % force_unicode(opts.verbose_name_plural),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        if extra_context:
            context.update(extra_context)
        return self.render_add_many_form(request, context, form_url=form_url)
    add_many_view = transaction.atomic(add_many_view)

    def get_urls(self):
        from django.conf.urls import patterns, url
        urlpatterns = super(ImageAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = patterns('',
            url(r'^addmany/$',
                wrap(self.add_many_view),
                name='%s_%s_addmany' % info),
        ) + urlpatterns
        return urlpatterns


admin.site.register(Image, ImageAdmin)
