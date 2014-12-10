from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='openlivinglab/frontpage.html')),
    url(r'^samples$','smartlivinglab.samples.views.index', name='openlivinglab_samples_index'),    
    (r'^samples/', include('smartlivinglab.samples.urls')),    
    url(r'^api$', RedirectView.as_view(url='/api/v1', permanent=False),name='api_redirect'),
    url(r'^api/v1/', include('smartlivinglab.urls_v1')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token',name='rest_framework')
)
