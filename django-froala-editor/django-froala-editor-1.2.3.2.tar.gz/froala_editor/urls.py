from django.conf.urls import patterns, url
from froala_editor import views

urlpatterns = patterns('',
                       url(r'^image_upload/$', views.image_upload, name='froala_editor_image_upload'),
)
