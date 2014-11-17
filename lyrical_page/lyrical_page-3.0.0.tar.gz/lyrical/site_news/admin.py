import datetime

from django.conf import settings
from django.contrib.admin import ModelAdmin, site
from lyrical.site_content.settings import ENABLE_BUILTIN_MEDIA, RTE_CONFIG_URI

from lyrical.site_news.models import SiteNewsCategory, SiteNewsArticle

site.register(SiteNewsCategory)


class SiteNewsArticleAdmin(ModelAdmin):
    list_display = ('title', 'sitenewscategory', 'author', 'published', 'publish_date')
    list_filter = ('sitenewscategory', 'author', 'published',)

    def save_model(self, request, obj, form, change):
        if obj.published:
            obj.publish_date = datetime.datetime.now()
        else:
            obj.publish_date = None
        obj.save()

    if ENABLE_BUILTIN_MEDIA:
        class Media:
            css = {'all': ('site_content/css/grappelli-tinymce.css',)}
            js = (getattr(settings, 'STATIC_URL', '') + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js', RTE_CONFIG_URI)


site.register(SiteNewsArticle, SiteNewsArticleAdmin)
