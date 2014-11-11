from django.conf.urls import patterns, url
from .views import DeployView, DeployStatusView

urlpatterns = patterns(
    '',
    url(r'^deploy/status/(?P<secret_key>.+)$', DeployStatusView.as_view(),
        name='ftpdeploy_deploy_status'),
    url(r'^deploy/(?P<secret_key>.+)$', DeployView.as_view(),
        name='ftpdeploy_deploy'),
)
