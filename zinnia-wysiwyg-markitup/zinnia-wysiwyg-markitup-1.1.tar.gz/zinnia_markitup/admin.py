"""EntryAdmin for zinnia-markitup"""
from django.forms import Media
from django.conf.urls import url
from django.conf.urls import patterns
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
from django.contrib.staticfiles.storage import staticfiles_storage

from zinnia import settings
from zinnia.models import Entry
from zinnia.admin.entry import EntryAdmin


class EntryAdminMarkItUpMixin(object):
    """
    Mixin adding WYMeditor for editing Entry.content field.
    """

    def markitup(self, request):
        """
        View for serving the config of MarkItUp.
        """
        return TemplateResponse(
            request, 'admin/zinnia/entry/markitup.js',
            content_type='application/javascript')

    @csrf_exempt
    def content_preview(self, request):
        """
        Admin view to preview Entry.content in HTML,
        useful when using markups to write entries.
        """
        data = request.POST.get('data', '')
        entry = self.model(content=data)
        return TemplateResponse(
            request, 'admin/zinnia/entry/preview.html',
            {'preview': entry.html_content})

    def get_urls(self):
        """
        Overload the admin's urls for MarkItUp.
        """
        entry_admin_urls = super(EntryAdminMarkItUpMixin, self).get_urls()
        urls = patterns(
            '',
            url(r'^markitup/$',
                self.admin_site.admin_view(self.markitup),
                name='zinnia_entry_markitup'),
            url(r'^markitup/preview/$',
                self.admin_site.admin_view(self.content_preview),
                name='zinnia_entry_markitup_preview')
        )
        return urls + entry_admin_urls

    def _media(self):
        """
        The medias needed to enhance the admin page.
        """
        def static_url(url):
            return staticfiles_storage.url('zinnia_markitup/%s' % url)

        media = super(EntryAdminMarkItUpMixin, self).media

        media += Media(
            js=(static_url('js/jquery.min.js'),
                static_url('js/markitup/jquery.markitup.js'),
                static_url('js/markitup/sets/%s/set.js' % (
                    settings.MARKUP_LANGUAGE)),
                reverse('admin:zinnia_entry_markitup')),
            css={'all': (
                static_url('js/markitup/skins/django/style.css'),
                static_url('js/markitup/sets/%s/style.css' % (
                    settings.MARKUP_LANGUAGE)))}
        )
        return media
    media = property(_media)


class EntryAdminMarkItUp(EntryAdminMarkItUpMixin,
                         EntryAdmin):
    """
    Enrich the default EntryAdmin with MarkItUp.
    """
    pass


if settings.ENTRY_BASE_MODEL == 'zinnia.models_bases.entry.AbstractEntry':
    admin.site.unregister(Entry)
    admin.site.register(Entry, EntryAdminMarkItUp)
