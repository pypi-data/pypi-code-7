from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from ftp_deploy.models import Notification


class NotificationForm(forms.ModelForm):

    fields = ['name', 'success', 'fail', 'commit_user', 'deploy_user']

    success = forms.CharField(
        widget=forms.TextInput(
            attrs={'size': '150'}), help_text='Comma separated list of emails',
        required=False)
    fail = forms.CharField(
        widget=forms.TextInput(
            attrs={'size': '150'}), help_text='Comma separated list of emails',
        required=False)
    deploy_user = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=((0, 'Success'), (1, 'Fail')), required=False)
    commit_user = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=((0, 'Success'), (1, 'Fail')), required=False)

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)

        self.helper_header = FormHelper()
        self.helper_header.html5_required = True
        self.helper_header.form_tag = False

        self.helper_header.layout = Layout(
            'name',
            Field('success', type="hidden"),
            Field('fail', type="hidden")
        )

        self.helper_user = FormHelper()
        self.helper_user.form_tag = False

        self.helper_user.layout = Layout(
            Field('deploy_user',
                  template='ftp_deploy/notification/form-user-field.html'),
            Field('commit_user',
                  template='ftp_deploy/notification/form-user-field.html')
        )

    class Meta:
        model = Notification
