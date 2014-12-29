from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^fighter/$', TemplateView.as_view(template_name='fighter.html'), name='fighter'),
)
