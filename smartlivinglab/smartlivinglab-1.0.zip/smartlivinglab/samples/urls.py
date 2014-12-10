from django.conf.urls import patterns, include, url


urlpatterns = patterns('smartlivinglab.samples.views',
    url(r'^(?P<sensor_code>[^/]+)$','sensor_index', name='openlivinglab_samples_sensor_index'),
)                      

