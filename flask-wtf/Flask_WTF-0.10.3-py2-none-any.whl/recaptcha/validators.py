try:
    import urllib2 as http
except ImportError:
    # Python 3
    from urllib import request as http

from flask import request, current_app
from wtforms import ValidationError
from werkzeug import url_encode
from .._compat import to_bytes

RECAPTCHA_VERIFY_SERVER = 'https://www.google.com/recaptcha/api/verify'

__all__ = ["Recaptcha"]


class Recaptcha(object):
    """Validates a ReCaptcha."""

    _error_codes = {
        'invalid-site-public-key': 'The public key for reCAPTCHA is invalid',
        'invalid-site-private-key': 'The private key for reCAPTCHA is invalid',
        'invalid-referrer': (
            'The public key for reCAPTCHA is not valid for '
            'this domainin'
        ),
        'verify-params-incorrect': (
            'The parameters passed to reCAPTCHA '
            'verification are incorrect'
        )
    }

    def __init__(self, message=u'Invalid word. Please try again.'):
        self.message = message

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.json:
            challenge = request.json.get('recaptcha_challenge_field', '')
            response = request.json.get('recaptcha_response_field', '')
        else:
            challenge = request.form.get('recaptcha_challenge_field', '')
            response = request.form.get('recaptcha_response_field', '')
        remote_ip = request.remote_addr

        if not challenge or not response:
            raise ValidationError(field.gettext(self.message))

        if not self._validate_recaptcha(challenge, response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

    def _validate_recaptcha(self, challenge, response, remote_addr):
        """Performs the actual validation."""
        try:
            private_key = current_app.config['RECAPTCHA_PRIVATE_KEY']
        except KeyError:
            raise RuntimeError("No RECAPTCHA_PRIVATE_KEY config set")

        data = url_encode({
            'privatekey': private_key,
            'remoteip':   remote_addr,
            'challenge':  challenge,
            'response':   response
        })

        response = http.urlopen(RECAPTCHA_VERIFY_SERVER, to_bytes(data))

        if response.code != 200:
            return False

        rv = [l.strip() for l in response.readlines()]

        if rv and rv[0] == to_bytes('true'):
            return True

        if len(rv) > 1:
            error = rv[1]
            if error in self._error_codes:
                raise RuntimeError(self._error_codes[error])

        return False
