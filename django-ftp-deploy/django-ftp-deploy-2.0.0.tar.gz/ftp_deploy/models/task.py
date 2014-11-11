
from django.db import models

from .service import Service


class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    service = models.ForeignKey(Service)
    active = models.BooleanField(default=False)

    class Meta:
        app_label = 'ftp_deploy'
        db_table = 'ftp_deploy_task'
