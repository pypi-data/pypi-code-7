# -*- coding: utf-8 -*-
from django.db import models


class QueueItemManager(models.Manager):
    def append(self, video):
        return self.create(related_video=video)

    def get_next(self):
        try:
            return self.get_queryset().select_related().\
                filter(error=False).order_by('uploaded')[0]
        except IndexError:
            return None


class VideoManager(models.Manager):
    pass
