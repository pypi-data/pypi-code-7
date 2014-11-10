"""URLs for the aps_bom app."""
from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^cbom/upload/$', views.CBOMUploadView.as_view(),
        name='aps_bom_cbom_upload'),
    url(r'^bom/download/(?P<cbom_pk>\d+)/$', views.CBOMDownloadView.as_view(),
        name='aps_bom_cbom_download'),
    url(r'^bom/download/$', views.CBOMDownloadView.as_view(),
        name='aps_bom_cbom_download'),
    url(r'^bom/upload/$', views.BOMUploadView.as_view(),
        name='aps_bom_bom_upload'),
    url(r'^ddl-ajax/', views.DropDownChoicesAJAXView.as_view(),
        name='aps_bom_ddl_ajax'),
)
