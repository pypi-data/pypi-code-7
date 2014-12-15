# -*- coding: utf-8 -*-
import os
from mediastore.conf import settings

class SettingsProxy(object):
    def __init__(self, settings, defaults):
        self.settings = settings
        self.defaults = defaults

    def __getattr__(self, attr):
        try:
            return getattr(self.settings, attr)
        except AttributeError:
            try:
                return getattr(self.defaults, attr)
            except AttributeError:
                raise AttributeError, 'settings object has no attribute "%s"' % attr


class defaults(object):
    MEDIASTORE_VIDEO_UPLOAD_DIR = os.path.join(
        settings.MEDIASTORE_FS_PREFIX, 'video')
    MEDIASTORE_VIDEO_THUMBNAIL_UPLOAD_DIR = os.path.join(
        settings.MEDIASTORE_FS_PREFIX, 'video', 'thumbnails')
    MEDIASTORE_VIDEO_AUTO_THUMBNAIL_UPLOAD_DIR = os.path.join(
        settings.MEDIASTORE_FS_PREFIX, 'video', 'generated_thumbnails')

    MEDIASTORE_VIDEO_WIDTH = '640'
    MEDIASTORE_VIDEO_HEIGHT = '480'
    MEDIASTORE_VIDEO_BITRATE = '586000'
    MEDIASTORE_VIDEO_AUDIO_BITRATE = '44100'
    MEDIASTORE_VIDEO_THUMBNAIL_POS = '10'
    MEDIASTORE_VIDEO_BACKEND = 'mediastore.mediatypes.video.convert.ffmpeg.FFmpegConverter'

    MEDIASTORE_VIDEO_FFMPEG_CROP = False

    MEDIASTORE_VIDEO_FFMPEG_BIN = 'ffmpeg'
    MEDIASTORE_VIDEO_FFMPEG_ARGS = [
        '-i', '%(input)s',
        '-f', 'flv',
        '-vcodec', 'flv',
        '-acodec', 'adpcm_swf',
        '-b', '%(bitrate)s',
        '-ar', '%(audio_bitrate)s',
        '-croptop', '%(croptop)s',
        '-cropbottom', '%(cropbottom)s',
        '-cropleft', '%(cropleft)s',
        '-cropright', '%(cropright)s',
        '-padtop', '%(padtop)s',
        '-padbottom', '%(padbottom)s',
        '-padleft', '%(padleft)s',
        '-padright', '%(padright)s',
        '-s', '%(width)sx%(height)s',
        '-y', '%(output)s',
    ]
    MEDIASTORE_VIDEO_FFMPEG_THUMBNAIL_BIN = 'ffmpeg'
    MEDIASTORE_VIDEO_FFMPEG_THUMBNAIL_ARGS = [
        '-i', '%(input)s',
        '-f', 'mjpeg',
        '-ss', '%(thumbnail_pos)s',
        '-vframes', '1',
        '-croptop', '%(croptop)s',
        '-cropbottom', '%(cropbottom)s',
        '-cropleft', '%(cropleft)s',
        '-cropright', '%(cropright)s',
        '-padtop', '%(padtop)s',
        '-padbottom', '%(padbottom)s',
        '-padleft', '%(padleft)s',
        '-padright', '%(padright)s',
        '-s', '%(width)sx%(height)s',
        '-an',
        '-y', '%(output)s',
    ]


from django.conf import settings as django_settings
settings = SettingsProxy(django_settings, defaults)
