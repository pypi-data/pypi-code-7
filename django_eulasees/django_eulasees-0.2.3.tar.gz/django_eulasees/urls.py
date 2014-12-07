from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from django_eulasees import api

urlpatterns = [
    url(r'^raweulas/$', api.RawEulaList.as_view()),
    url(r'^raweulas/(?P<pk>[0-9]+)/$', api.RawEulaList.as_view(), name='raweula-detail'),

    url(r'^eulasnippets/$', api.EulaSnippetList.as_view()),
    url(r'^eulasnippets/(?P<pk>[0-9]+)/$', api.EulaSnippetList.as_view(), name='eulasnippet-detail'),

    url(r'^tags/$', api.TagList.as_view()),
    url(r'^tags/(?P<pk>[0-9]+)/$', api.TagList.as_view(), name='tag-detail'),
    
    url(r'^tagicons/$', api.TagIconList.as_view()),
    url(r'^tagicons/(?P<pk>[0-9]+)/$', api.TagIconList.as_view(), name='tagicon-detail'),
    
    url(r'^tageulas/$', api.TagEulaList.as_view()),
    url(r'^tageulas/(?P<pk>[0-9]+)/$', api.TagEulaList.as_view(), name='tag-detail'),
    
    url(r'^snippettags/$', api.SnippetTagList.as_view()),
    url(r'^snippettags/(?P<pk>[0-9]+)/$', api.SnippetTagList.as_view(), name='snippettag-detail'),

    url(r'^snippetsforeula/(?P<pk>[0-9]+)/$$', api.SnippetsForEula.as_view()),

    url(r'^tagsforsnippet/(?P<pk>[0-9]+)/$$', api.TagsForSnippet.as_view()),
    url(r'^tagsforeula/(?P<pk>[0-9]+)/$$', api.TagsForEula.as_view()),

    url(r'^eulasfortag/(?P<pk>[0-9]+)/$$', api.EulasForTag.as_view()),

    url(r'^snippettagsforeula/(?P<pk>[0-9]+)/$$', api.SnippetTagsForEula.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
