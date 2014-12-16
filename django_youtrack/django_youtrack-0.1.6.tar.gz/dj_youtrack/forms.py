# -*- encoding: utf-8 -*-
from django import forms
from django.conf import settings
from youtrack.connection import Connection
from youtrack import YouTrackException


class IssueForm(forms.Form):
    email = forms.EmailField()
    description = forms.CharField(widget=forms.Textarea)

    def __init__(self, project, **kwargs):
        self.project = project
        super(IssueForm, self).__init__(**kwargs)

    def submit(self):
        try:
            connection = Connection(settings.YOUTRACK_URL, settings.YOUTRACK_LOGIN, settings.YOUTRACK_PASSWORD)
            response, content = connection.createIssue(self.project, assignee=None,
                                                       summary=u'Issue from feedback form',
                                                       description=self.cleaned_data['description'])
            print response
            issue_id = response['location'].split('/')[-1]
            connection.executeCommand(issue_id, 'Customer email ' + self.cleaned_data['email'])
            return True
        except YouTrackException:
            return False