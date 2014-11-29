from formskit.formvalidators import FormValidator
from formskit.validators import NotEmpty

from haplugin.formskit import PostForm


class EmailMustExists(FormValidator):

    message = "EmailMustExists"

    def validate(self):
        db = self.form.db

        email = self.form.get_value('email')
        user_cls = self.form.request.user_cls
        user = db.query(user_cls).filter_by(email=email).first()
        self.form.user = user
        return not user is None


class PasswordMustMatch(FormValidator):

    message = "PasswordMustMatch"

    def validate(self):
        data = self.form.get_data_dict(True)
        user_cls = self.form.request.user_cls
        db = self.form.request.db
        self.user = (
            db.query(user_cls).filter_by(email=data['email']).one()
        )
        return self.user.validate_password(data['password'])


class LoginForm(PostForm):

    def create_form(self):
        self.add_field('email', label='E-mail', validators=[NotEmpty()])
        self.add_field('password', label='Hasło', validators=[NotEmpty()])

        self.add_form_validator(EmailMustExists())
        self.add_form_validator(PasswordMustMatch())

    def submit(self):
        self.session['user_id'] = self.user.id
