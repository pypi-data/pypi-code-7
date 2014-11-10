"""URLs for the aps_purchasing app."""
from django.conf.urls import patterns, url

from .views import QuotationUploadView, ReportView


urlpatterns = patterns(
    '',
    url(r'^quotation-upload/$', QuotationUploadView.as_view(),
        name='aps_purchasing_quotation_upload'),
    url(r'^report/(?P<pk>\d+)/$', ReportView.as_view(),
        name='aps_purchasing_report'),
    url(r'^report/', ReportView.as_view(),
        name='aps_purchasing_report'),
)
