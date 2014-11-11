import json
from django.db import models

from ftp_deploy.utils.repo import commits_parser
from .service import Service


class Log(models.Model):
    service = models.ForeignKey(Service, blank=True)
    payload = models.TextField()
    user = models.CharField(max_length=200)
    status = models.BooleanField(default=False)
    status_message = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    skip = models.BooleanField(default=False)

    def commits_info(self):
        commits = json.loads(self.payload)['commits']
        return commits_parser(commits, self.service.repo_source).commits_info()

    class Meta:
        ordering = ('-created',)
        app_label = 'ftp_deploy'
        db_table = 'ftp_deploy_log'
