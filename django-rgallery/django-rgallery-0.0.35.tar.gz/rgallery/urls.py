# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rgallery.views import (Photos,
                            Videos,
                            PhotosFolder,
                            PhotoDelete,
                            PhotoAdd,
                            PhotosTag,
                            PhotoAddTag,
                            PhotoGetVideo,
                            PhotoChangeStatus,
                            PhotoDownload)

urlpatterns = patterns('',
    url(r'^$', Photos.as_view(), name='app_gallery-gallery'),
    url(r'^page/(?P<page>\d+)/$', Photos.as_view(), name='app_gallery-gallery-page'),
    url(r'^photo/del/$', PhotoDelete.as_view(), name='app_gallery-photo-del'),
    url(r'^photo/add/$', PhotoAdd.as_view(), name='app_gallery-photo-add'),
    url(r'^photo/changestatus/$', PhotoChangeStatus.as_view(), name='app_gallery-photo-changestatus'),
    url(r'^photo/download/$', PhotoDownload.as_view(), name='app_gallery-photo-download'),
    url(r'^photos/tag/(?P<slug>[-\w]+)/$', PhotosTag.as_view(), name='app_gallery-photos-tag'),
    url(r'^photo/add/tag/$', PhotoAddTag.as_view(), name='app_gallery-photo-add-tag'),
    url(r'^photo/get_video/$', PhotoGetVideo.as_view(), name='app_gallery-photo-getvideo'),
    url(r'^videos/$', Videos.as_view(), name='app_gallery-videos'),
    url(r'^videos/page/(?P<page>\d+)/$', Videos.as_view(), name='app_gallery-videos-page'),
    url(r'^(?P<folder>[-_A-Za-z0-9]+)/$', PhotosFolder.as_view(), name='app_gallery-folder'),
)
