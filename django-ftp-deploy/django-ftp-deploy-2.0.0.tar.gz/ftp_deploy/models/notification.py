from django.db import models


class Notification(models.Model):
    name = models.CharField(max_length=200, unique=True)
    success = models.TextField(blank=True)
    fail = models.TextField(blank=True)
    commit_user = models.CharField('Commit User', max_length=50, blank=True)
    deploy_user = models.CharField('Deploy User', max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_email_list(self):
        emails = dict()

        for email in self.get_success():
            emails[email] = dict()
            emails[email]['success'] = True

        for email in self.get_fail():
            try:
                emails[email]['fail'] = True
            except KeyError:
                emails[email] = dict()
                emails[email]['fail'] = True

        return emails

    def get_success(self):
        return list(filter(None, self.success.split(',')))

    def get_fail(self):
        return list(filter(None, self.fail.split(',')))

    def commit_user_success(self):
        return True if '0' in self.commit_user else False

    def commit_user_fail(self):
        return True if '1' in self.commit_user else False

    def deploy_user_success(self):
        return True if '0' in self.deploy_user else False

    def deploy_user_fail(self):
        return True if '1' in self.deploy_user else False

    class Meta:
        ordering = ('name',)
        app_label = 'ftp_deploy'
        db_table = 'ftp_deploy_notification'
