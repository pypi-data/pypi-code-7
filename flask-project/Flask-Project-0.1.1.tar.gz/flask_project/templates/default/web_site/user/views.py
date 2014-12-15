from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import user_blueprint as bp
from .. import db
from .models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, ResendConfirmForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            if not user.confirmed:
                return render_template('user/unconfirmed.html', username=user.username)
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.', 'warning')
    return render_template('user/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'user/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.', 'info')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)


@bp.route('/confirm/<email>/<token>')
def confirm(email, token):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('%s is not registered' % email, 'warning')
        return redirect(url_for('user.register'))
    if user.confirmed:
        return redirect(url_for('main.index'))
    if user.confirm(token):
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'warning')
    return redirect(url_for('user.login'))


@bp.route('/resend_confirm', methods=['GET', 'POST'])
def resend_confirm():
    form = ResendConfirmForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'user/email/confirm', user=user, token=token)
        flash('A new confirmation email has been sent to you by email.', 'info')
        return redirect(url_for('user.resend_confirm'))
    return render_template("user/resend_confirm.html", form=form)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.', 'info')
            logout_user()
            return redirect(url_for('user.login'))
        else:
            flash('Invalid password.', 'warning')
    return render_template("user/change_password.html", form=form)


@bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'user/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.', 'info')
        return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', form=form)


@bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.', 'success')
            return redirect(url_for('user.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('user/reset_password.html', form=form)


@bp.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'user/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'warning')
    return render_template("user/change_email.html", form=form)


@bp.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'info')
    else:
        flash('Invalid request.', 'warning')
    return redirect(url_for('main.index'))
