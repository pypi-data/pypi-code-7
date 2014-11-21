from django.conf.urls import *

urlpatterns = patterns('',
    (r'^test/', 'hashphrase.views.hash_link_test'),
    (r'^(?P<key>.*)/$', 'hashphrase.views.hash_link'),
)