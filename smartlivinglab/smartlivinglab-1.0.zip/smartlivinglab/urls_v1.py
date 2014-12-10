from django.conf.urls import patterns, url

from smartlivinglab import views

urlpatterns = patterns('smartlivinglab.views',

    url(r'^$', 'api_root'),
    url(r'^nodes/$',
        views.NodeList.as_view(),
        name='node-list'),
    url(r'^node/(?P<pk>[0-9]+)/$',
        views.NodeDetail.as_view(),
        name='node-detail'),
    url(r'^sensor/$',
        views.SensorList.as_view(),
        name='sensor-list'),
    url(r'^sensor/(?P<pk>[0-9]+)$',
        views.SensorDetail.as_view(),
        name='sensor-detail'),
    url(r'add$',
        views.ValueView.as_view(),
        name='add-data'),
)
