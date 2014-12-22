from pyramid.session import check_csrf_token
from hatak.unpackrequest import unpack

from formskit import Form
from formskit.formvalidators import FormValidator


class PostForm(Form):

    def __init__(self, request):
        self.request = request
        unpack(self, self.request)
        super().__init__()

        self.add_form_validator(CsrfMustMatch())
        self.init_csrf()

    def reset(self):
        super().reset()
        self.init_csrf()

    def init_csrf(self):
        self.add_field('csrf_token')
        self.set_value('csrf_token', self.session.get_csrf_token())

    def __call__(self):
        return super().__call__(self.request.POST.dict_of_lists())


class CsrfMustMatch(FormValidator):

    message = "CSRF token do not match!"

    def validate(self):
        self.form.POST['csrf_token'] = self.form.get_value('csrf_token')
        return check_csrf_token(self.form.request, raises=False)
