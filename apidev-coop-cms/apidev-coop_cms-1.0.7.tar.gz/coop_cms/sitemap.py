# -*- coding:utf-8 -*-
from django.conf.urls import url
from django.contrib.sitemaps import Sitemap
from coop_cms.settings import get_article_class
from coop_cms.models import BaseArticle
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

class ViewSitemap(Sitemap):
    view_names = []
    
    def items(self):
        
        class Klass(object):
            def __init__(self, name):
                self.name = name
            
            def get_absolute_url(self):
                return reverse(self.name)
            
        return [Klass(x) for x in self.view_names]

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        Article = get_article_class()
        return Article.objects.filter(
            publication=BaseArticle.PUBLISHED, sites=Site.objects.get_current())

    def lastmod(self, obj):
        return obj.modified

def get_sitemaps(langs=None):
    if 'localeurl' in settings.INSTALLED_APPS:
        from localeurl.sitemaps import LocaleurlSitemap
        class LocaleArticleSitemap(LocaleurlSitemap, ArticleSitemap): pass
        sitemaps = {}
        lang_codes = langs or [code for (code, _x) in settings.LANGUAGES]
        for code in lang_codes:
            sitemaps['coop_cms_'+code] = LocaleArticleSitemap(code) 
    else:
        sitemaps = {
            'coop_cms': ArticleSitemap,
        }
    return sitemaps
    
urlpatterns = (
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': get_sitemaps()}, name="coop_cms_sitemap"),
)