from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Username', 'required': 'required'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            render_value=False,
            attrs={'placeholder': 'Password', 'required': 'required'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-signin'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            'username',
            'password',
            Submit('login', 'Log in', css_class='btn-lg btn-block'),
        )
