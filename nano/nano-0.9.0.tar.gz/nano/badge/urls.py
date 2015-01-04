from django.conf.urls import *

urlpatterns = patterns('nano.badge.views',
        url(r'^$',                        'list_badges', {}, 'badge-list'),
        url(r'^(?P<pk>[0-9]+)/$',  'show_badge', {}, 'badge-detail'),
)
