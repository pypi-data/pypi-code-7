from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView


urlpatterns = patterns("",

    url(
        r"^mip-error/$",
        TemplateView.as_view(template_name="error.html"),
        name="mip-error"
    ),

)

handler500 = "maintenance_in_progress.views.server_error"
