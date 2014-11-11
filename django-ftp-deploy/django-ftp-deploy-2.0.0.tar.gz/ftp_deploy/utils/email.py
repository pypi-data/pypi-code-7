import json

from abc import ABCMeta, abstractmethod
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ftp_deploy.conf import *
from .repo import commits_parser, repository_parser


class notification():

    """Notification abstract class, take three arguments, host,
        service object and payload json string"""
    __metaclass__ = ABCMeta

    def __init__(self, host, service, payload):
        self.host = host
        self.service = service
        self.payload = json.loads(payload)
        self.commits = self.payload['commits']
        self.from_email = 'noreply@ftpdeploy.com'
        self.repo = repository_parser(self.payload, self.service)
        self.send()

    @property
    def template_html(self):
        raise NotImplementedError

    @property
    def template_text(self):
        raise NotImplementedError

    @abstractmethod
    def subject(self):
        pass

    @abstractmethod
    def emails(self):
        pass

    @abstractmethod
    def context(self):
        pass

    def send(self):
        """Sent method process emails from list returned by emails() method"""

        for recipient in self.emails():
            text_content = render_to_string(self.template_text, self.context())
            html_content = render_to_string(self.template_html, self.context())

            msg = EmailMultiAlternatives(self.subject(), text_content,
                                         self.from_email, [recipient])
            msg.attach_alternative(html_content, "text/html")
            msg.send()


class notification_success(notification):

    """Notification class for success"""

    template_html = 'ftp_deploy/email/email_success.html'
    template_text = 'ftp_deploy/email/email_success.txt'

    def subject(self):
        return '%s - Deploy Successfully' % self.service

    def emails(self):
        emails_list = list()
        notifications = self.service.notification

        if notifications:
            emails_list += notifications.get_success()

            if notifications.deploy_user_success():
                emails_list += self.repo.deploy_email()

            if notifications.commit_user_success():
                emails_list += commits_parser(
                    self.commits, self.service.repo_source).email_list()

        return list(set(emails_list))

    def context(self):
        context = dict()
        context['service'] = self.service
        context['host'] = self.host
        context['commits_info'] = commits_parser(
            self.commits, self.service.repo_source).commits_info()
        context['files_added'], context['files_modified'], context[
            'files_removed'] = commits_parser(
            self.commits, self.service.repo_source).file_diff()

        return context


class notification_fail(notification):

    """Notification class for fail"""

    template_html = 'ftp_deploy/email/email_fail.html'
    template_text = 'ftp_deploy/email/email_fail.txt'

    def __init__(self, host, service, payload, error):
        self.error = error
        super(notification_fail, self).__init__(host, service, payload)

    def subject(self):
        return '%s - Deploy Fail' % self.service

    def emails(self):
        emails_list = list()
        notifications = self.service.notification

        if notifications:

            emails_list += notifications.get_fail()

            if notifications.deploy_user_fail():
                emails_list += self.repo.deploy_email()

            if notifications.commit_user_fail():
                emails_list += commits_parser(
                    self.commits, self.service.repo_source).email_list()

        return list(set(emails_list))

    def context(self):
        context = dict()
        context['host'] = self.host
        context['service'] = self.service
        context['error'] = self.error
        return context
