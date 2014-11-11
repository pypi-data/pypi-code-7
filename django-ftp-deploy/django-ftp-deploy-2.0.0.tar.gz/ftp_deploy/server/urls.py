from django.conf.urls import patterns, url
from .views import DashboardView, LogView, LogSkipDeployView, RepoAPIView
from .views import (ServiceManageView, ServiceRestoreView, ServiceEditView,
                    ServiceAddView, ServiceStatusView, ServiceDeleteView,
                    ServiceNotificationView)
from .views import (NotificationView, NotificationAddView,
                    NotificationEditView, NotificationDeleteView)
from .views import loginView, logoutView


urlpatterns = patterns(
    '',
    url(r'^$', loginView.as_view(), name='ftpdeploy_login'),
    url(r'^logout/$', logoutView.as_view(), name='ftpdeploy_logout'),

    url(r'^dashboard/$', DashboardView.as_view(), name='ftpdeploy_dashboard'),

    url(r'^service/add$', ServiceAddView.as_view(),
        name='ftpdeploy_service_add'),
    url(r'^service/(?P<pk>\d+)/manage$', ServiceManageView.as_view(),
        name='ftpdeploy_service_manage'),
    url(r'^service/(?P<pk>\d+)/edit$', ServiceEditView.as_view(),
        name='ftpdeploy_service_edit'),
    url(r'^service/(?P<pk>\d+)/delete$', ServiceDeleteView.as_view(),
        name='ftpdeploy_service_delete'),
    url(r'^service/(?P<pk>\d+)/status/$', ServiceStatusView.as_view(),
        name='ftpdeploy_service_status'),
    url(r'^service/(?P<pk>\d+)/restore/$', ServiceRestoreView.as_view(),
        name='ftpdeploy_service_restore'),
    url(r'^service/(?P<pk>\d+)/notification/$', ServiceNotificationView.as_view(),
        name='ftpdeploy_service_notification'),
    url(r'^service/(?P<pk>\d+)/repoapi/(?P<repo>.{2})/$', RepoAPIView.as_view(),
        name='ftpdeploy_repo_api'),

    url(r'^log/$', LogView.as_view(), name='ftpdeploy_log'),
    url(r'^log/(?P<pk>\d+)/skip/$', LogSkipDeployView.as_view(),
        name='ftpdeploy_log_skip'),

    url(r'^notification/$', NotificationView.as_view(),
        name='ftpdeploy_notification'),
    url(r'^notification/add$', NotificationAddView.as_view(),
        name='ftpdeploy_notification_add'),
    url(r'^notification/(?P<pk>\d+)/edit$', NotificationEditView.as_view(),
        name='ftpdeploy_notification_edit'),
    url(r'^notification/(?P<pk>\d+)/delete$', NotificationDeleteView.as_view(),
        name='ftpdeploy_notification_delete'),
)
