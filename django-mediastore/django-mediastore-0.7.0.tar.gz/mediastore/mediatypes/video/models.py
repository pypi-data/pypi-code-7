# -*- coding: utf-8 -*-
import os
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save
from mediastore.mediatypes.video.conf import settings
from mediastore.models import Media
from mediastore.mediatypes.video.managers import QueueItemManager, VideoManager
from mediastore.mediatypes.video import convert


def get_file_extension(file):
    name, ext = os.path.splitext(file.name)
    return ext


class Video(Media):
    help_text = _('Stores a flash video file and a preview thumbnail.')

    file = models.FileField(_('video'),
        upload_to=settings.MEDIASTORE_VIDEO_UPLOAD_DIR)
    thumbnail = models.ImageField(_('video thumbnail'),
        null=True, blank=True,
        upload_to=settings.MEDIASTORE_VIDEO_THUMBNAIL_UPLOAD_DIR)
    generated_thumbnail = models.ImageField(_('generated video thumbnail'),
        null=True, blank=True,
        upload_to=settings.MEDIASTORE_VIDEO_AUTO_THUMBNAIL_UPLOAD_DIR)
    is_ready = models.BooleanField(default=False)

    objects = VideoManager()

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    def get_thumbnail(self):
        return self.thumbnail or self.generated_thumbnail or None


class QueueItem(models.Model):
    '''
    A queued video file which should be converted into
    the flv format.
    '''
    related_video = models.ForeignKey(Video)
    uploaded = models.DateTimeField(auto_now_add=True)
    error = models.BooleanField(default=False)
    error_message = models.TextField(default='')

    objects = QueueItemManager()

    class Meta:
        app_label = 'mediastore'

    def __unicode__(self):
        return u"Queue: %s" % unicode(self.related_video)

    def append_error_message(self, backend, exception):
        self.error_message += (
            '%(sep)s\n'
            '%(date)s, convertion failed:\n'
            '%(sep)s\n'
            'stdout:\n\n'
            '%(stdout)s\n'
            '%(sep)s\n'
            'stderr:\n\n'
            '%(stderr)s\n'
            '%(sep)s\n\n' % {
                'date': datetime.now().isoformat(),
                'sep': '=' * 50,
                'stdout': backend.stdout,
                'stderr': backend.stderr,
            })


    def process_video(self, backend):
        self.error = False
        self.needs_processing = True

        path = self.related_video.file.path
        media_root = settings.MEDIA_ROOT
        if not media_root.endswith(os.sep):
            media_root += os.sep
        new_dir = os.path.join(media_root,
            settings.MEDIASTORE_VIDEO_UPLOAD_DIR)
        new_path = os.path.join(new_dir, '%s.flv' % self.related_video.pk)
        # create directories if they don't exist yet
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        try:
            backend.convert(path, new_path)
            os.remove(path)
            self.related_video.file = new_path[len(media_root):]
            self.related_video.is_ready = True
            self.related_video.save()
        except backend.ConvertionError, e:
            self.error = True
            self.append_error_message(backend, e)
            self.save()

    def process_thumbnail(self, backend):
        path = self.related_video.file.path
        media_root = settings.MEDIA_ROOT
        if not media_root.endswith(os.sep):
            media_root += os.sep
        try:
            thumb_dir = os.path.join(media_root,
                settings.MEDIASTORE_VIDEO_AUTO_THUMBNAIL_UPLOAD_DIR)
            thumb_path = os.path.join(thumb_dir,
                '%s.jpg' % self.related_video.pk)
            # create directories if they don't exist yet
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)
            backend.thumbnail(path, thumb_path)
            self.related_video.generated_thumbnail = thumb_path[len(media_root):]
        except backend.ConvertionError, e:
            self.append_error_message(backend, e)
        self.related_video.save()

    def process(self):
        print "process queue item #%s, file: %s ..." % (
            self.pk, self.related_video.file)
        Backend = convert.get_convert_backend()
        backend = Backend()

        self.error_message = ''
        self.process_video(backend)
        if not self.error and self.related_video.file:
            self.process_thumbnail(backend)
        if not self.error:
            self.delete()


def auto_add_to_queue(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    if created:
        QueueItem.objects.append(instance)
post_save.connect(auto_add_to_queue, sender=Video)
