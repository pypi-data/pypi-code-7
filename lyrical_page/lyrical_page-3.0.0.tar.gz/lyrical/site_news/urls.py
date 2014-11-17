from django.conf.urls import patterns, url

from lyrical.site_news.views import IndexListView, ArticleDetailView

urlpatterns = patterns('',
    url(r'^$', IndexListView.as_view(), name='news-index-list'),
    url(r'^(?P<sitenewscategory>[a-zA-Z0-9_-]+)/(?P<sitenewsarticle>[a-zA-Z0-9_-]+)/$', ArticleDetailView.as_view(), name='news-detail'),
)