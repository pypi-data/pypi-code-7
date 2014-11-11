import random
import string

from django.db import models
from django.core.urlresolvers import reverse

from ftp_deploy.utils.core import service_check
from ftp_deploy.conf import *
from .notification import Notification


def repo_choices():
    choices = tuple()
    if BITBUCKET_SETTINGS['username'] and BITBUCKET_SETTINGS['password']:
        choices = choices + (('bb', 'BitBucket'),)

    if GITHUB_SETTINGS['username'] and GITHUB_SETTINGS['password']:
        choices = choices + (('gh', 'Github'),)

    return choices


class Service(models.Model):

    ftp_host = models.CharField('Host', max_length=255)
    ftp_username = models.CharField('Username', max_length=50)
    ftp_password = models.CharField('Password', max_length=50)
    ftp_path = models.CharField('Path', max_length=255)

    repo_source = models.CharField('Source', max_length=10,
                                   choices=repo_choices())
    repo_name = models.CharField('Respository Name', max_length=50)
    repo_slug_name = models.SlugField('Respository Slug', max_length=50)
    repo_branch = models.CharField('Branch', max_length=50)
    repo_hook = models.BooleanField(default=False)

    secret_key = models.CharField('Secret Key', unique=True, max_length=30,
                                  default=''.join(random.choice(
                                      string.ascii_letters + string.digits) for x in range(30)))

    status = models.BooleanField(default=True)
    status_message = models.TextField()
    notification = models.ForeignKey(Notification, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.repo_name

    def deploys(self):
        return self.log_set.filter(status=True).count()

    def fail_deploys(self):
        return self.log_set.filter(status=False).filter(skip=False).count()

    def skipped_deploys(self):
        return self.log_set.filter(status=False).filter(skip=True).count()

    def latest_log_date(self):
        return self.log_set.latest('created').created

    def latest_log_user(self):
        return self.log_set.latest('created').user

    def hook_url(self):
        return reverse('ftpdeploy_deploy', kwargs={'secret_key':
                       self.secret_key})

    def get_logs_tree(self):
        """get logs tree for restore deploys.
            Include all logs since first fail apart of skiped."""
        first_fail_log = self.log_set.filter(status=0).order_by('pk')[:1]
        logs = self.log_set.filter(skip=0).filter(
            pk__gte=first_fail_log[0].pk).order_by('pk')
        return logs

    def lock(self):
        return self.task_set.filter(active=True).exists()

    def has_queue(self):
        return self.task_set.all().exists()

    def validate(self, **kwargs):

        message = list()
        fails, message = service_check(self).check_all()

        if fails[2]:
            self.repo_hook = False
        else:
            self.repo_hook = True

        if True in fails:
            self.status_message = '<br>'.join(message)
            self.status = False
        else:
            self.status = True
            self.status_message = ''

    class Meta:
        app_label = 'ftp_deploy'
        db_table = 'ftp_deploy_service'
