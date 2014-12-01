from django.conf.urls import patterns, url
from .views import BitBucketPostView


urlpatterns = patterns('trello_broker.views',
    url(r'^$',
        BitBucketPostView.as_view(),
        name='trello_broker_post'),
)
