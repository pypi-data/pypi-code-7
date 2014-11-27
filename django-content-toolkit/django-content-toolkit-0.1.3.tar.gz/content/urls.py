from django.conf.urls import patterns, url

from .views import ContentDetailView, ArticleDetailView
from .models import Page, Article


urlpatterns = patterns(
    '',
    url(regex=r'^(?P<slug>[-_\w]+)/$',
        view=ContentDetailView.as_view(model=Page),
        name='page-detail'
    ),
    url(regex=r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/$',
        view=ArticleDetailView.as_view(model=Article),
        name='article-detail'
    ),
    url(r'^(?P<slug>[-_\w]+)/$', ContentDetailView.as_view(), name='content-detail'),
)

