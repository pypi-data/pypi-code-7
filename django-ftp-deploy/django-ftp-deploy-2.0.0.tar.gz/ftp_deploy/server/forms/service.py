from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Div

from ftp_deploy.models import Service


class ServiceForm(forms.ModelForm):

    """Add/Edit service form"""

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'service-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.html5_required = True

        self.helper.layout = Layout(
            Fieldset('FTP Settings',
                     'ftp_host',
                     'ftp_username',
                     'ftp_password',
                     'ftp_path'
                     ),
            Fieldset('Repository',
                     Field('repo_source',
                           data_action=reverse(
                               'ftpdeploy_repo_api', args=(0, '__'))),
                     'repo_name',
                     'repo_slug_name',
                     'repo_branch'
                     ),
            Fieldset('Notification',
                     'notification'
                     ),
            Fieldset('Security',
                     'secret_key'
                     ),
            Div(
                Div(
                    Submit('save', 'Submit', css_class='pull-right'),
                    css_class='col-sm-12'
                ),
                css_class='row'
            )

        )

    def clean_ftp_path(self):
        data = self.cleaned_data['ftp_path']
        if not data.endswith('/'):
            data = '%s/' % data
        return data

    class Meta:
        model = Service
        exclude = ['status', 'status_date', 'status_message']
        widgets = {
            'ftp_password': forms.PasswordInput(render_value=True),
        }


class ServiceNotificationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ServiceNotificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'notification-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'hide'
        self.helper.field_class = 'col-sm-12'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            'notification'
        )

    class Meta:
        model = Service
        fields = ['notification']
