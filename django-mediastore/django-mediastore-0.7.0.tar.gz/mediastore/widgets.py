# -*- coding: utf-8 -*-
import os
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from mediastore import media_url
from mediastore.preview import preview_media
from mediastore.models import Media
from mediastore.utils import get_media_models
from mediastore.utils.models import order_queryset_by_pks

__all__ = ('MediaSelect', 'MediaSelectMultiple')


MEDIASELECT_CLASS = 'vForeignKeyMediaAdminField'
MEDIASELECTMULTIPLE_CLASS = 'vManyToManyMediaAdminField'


def _set_class(attrs, class_name):
    class_ = attrs.get('class', '')
    if class_:
        class_ += ' '
    class_ += class_name
    attrs['class'] = class_
    return attrs

def _get_string_as_list(value):
    if type(value) in (unicode, str):
        return (value,)
    return value


def _get_previews(values, field_name):
    output = []
    output.append('<div class="previews">')
    objs = order_queryset_by_pks(
        Media.objects.filter(pk__in=values),
        values)
    for obj in objs:
        output.append('<div class="preview preview-%s-%d">' % (field_name, obj.pk))
        output.append(preview_media(obj, {'size':'160px'}))
        output.append('<a href="javascript:deleteMediaRelation(\'%s\', \'id_%s\', \'%d\');" class="deletelink-media">' % (field_name, field_name, obj.pk))
        output.append('</a>')
        output.append('</div>')
    output.append('</div>')
    return output


class _AdminSiteDummy(object):
    _registry = {}


from django.contrib.admin.widgets import ForeignKeyRawIdWidget
class MediaSelect(ForeignKeyRawIdWidget):
    class Media:
        css = {
            'all': (media_url('css/select.css'),),
        }
        js = (
            media_url('js/jquery-1.3.2.min.js'),
            media_url('js/mediaselect.js'),
        )

    def __init__(self, rel, admin_site=_AdminSiteDummy(), *args, **kwargs):
        self.mediatype = kwargs.pop('mediatype', None)
        super(MediaSelect, self).__init__(rel, admin_site, *args, **kwargs)

    def url_parameters(self):
        params = super(MediaSelect, self).url_parameters()
        if self.mediatype:
            params['mediatype'] = self.mediatype
        return params

    def render(self, name, value, attrs=None):
        rel_to = self.rel.to
        if attrs is None:
            attrs = {}
        extra = []
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse('admin:%s_%s_select' %
                                    (rel_to._meta.app_label,
                                    rel_to._meta.module_name),
                                    current_app=self.admin_site.name)

            params = self.url_parameters()
            if params:
                url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])
            else:
                url = u''
            if "class" not in attrs:
                attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript code looks for this hook.
            # TODO: "lookup_id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            extra.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showMediaObjectLookupPopup(this);"> '
                            % (related_url, url, name))
            extra.append(u'<img src="%s" width="16" height="16" alt="%s" /></a>'
                            % (static('admin/img/selector-search.gif'), _('Lookup')))
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)] + extra
        if value:
            output.append(self.label_for_value(value))
        output.extend(_get_previews([value] if value else [], name))
        return mark_safe(u''.join(output))


from django.contrib.admin.widgets import ManyToManyRawIdWidget
class MediaSelectMultiple(ManyToManyRawIdWidget):
    class Media:
        css = {
            'all': (media_url('css/select.css'),),
        }
        js = (
            media_url('js/jquery-1.3.2.min.js'),
            media_url('js/jquery-ui-1.7.2.custom.min.js'),
            media_url('js/mediaselect.js'),
        )

    def __init__(self, rel, admin_site=_AdminSiteDummy(), *args, **kwargs):
        self.mediatype = kwargs.pop('mediatype', None)
        self.sorted = kwargs.pop('sorted', None)
        super(MediaSelectMultiple, self).__init__(rel, admin_site, *args, **kwargs)

    def url_parameters(self):
        params = self.base_url_parameters()
        if self.mediatype:
            params['mediatype'] = self.mediatype
        return params

    def render(self, name, value, attrs):
        rel_to = self.rel.to
        if attrs is None:
            attrs = {}
        extra = []
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse('admin:%s_%s_select_many' %
                                    (rel_to._meta.app_label,
                                    rel_to._meta.module_name),
                                    current_app=self.admin_site.name)

            params = self.url_parameters()
            if params:
                url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])
            else:
                url = u''
            if "class" not in attrs:
                attrs['class'] = 'vManyToManyRawIdAdminField' # The JavaScript code looks for this hook.
            # TODO: "lookup_id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            extra.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showMediaObjectLookupPopup(this);"> '
                            % (related_url, url, name))
            extra.append(u'<img src="%s" width="16" height="16" alt="%s" /></a>'
                            % (static('admin/img/selector-search.gif'), _('Lookup')))
        if self.sorted:
            attrs['class'] = '%s sorted' % attrs['class']
        strvalue = ','.join([force_unicode(v) for v in (value or [])])
        output = [super(ForeignKeyRawIdWidget, self).render(name, strvalue, attrs)] + extra
        if value:
            output.append(self.label_for_value(value))
        output.extend(_get_previews(value or [], name))
        return mark_safe(u''.join(output))


from django.forms.widgets import RadioFieldRenderer, RadioInput
from django.utils.encoding import force_unicode

class MediaTypeInput(RadioInput):
    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        model = get_media_models(*self.choice_value.split('.'))[0]
        output = [
            render_to_string('widgets/mediatypeselect/display_media_type.html', {
                'input': self.tag(),
                'icon_url': os.path.join(
                    settings.MEDIA_URL,
                    media_url('icons/128x128/%s.png' % model.media_type)),
                'label': mark_safe('<label%s>%s</label>' % (label_for, model._meta.verbose_name)),
                'label_for': label_for,
                'help_text': model.help_text,
            }),
        ]
        return mark_safe(''.join(output))


class MediaTypeRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield MediaTypeInput(self.name, self.value, self.attrs.copy(), choice, i)

    def render(self):
        return mark_safe(u'\n'.join([force_unicode(w) for w in self]))


class MediaTypeSelect(forms.RadioSelect):
    renderer = MediaTypeRenderer

    def __init__(self, *args, **kwargs):
        media_models = kwargs.setdefault('media_models', get_media_models())
        del kwargs['media_models']
        kwargs['choices'] = [
            ('%s.%s' % (model._meta.app_label.lower(), model._meta.object_name.lower()),) * 2
            for model in media_models]
        super(MediaTypeSelect, self).__init__(*args, **kwargs)
