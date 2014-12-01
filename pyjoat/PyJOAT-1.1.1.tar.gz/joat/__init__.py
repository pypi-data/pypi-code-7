from __future__ import unicode_literals

from calendar import timegm
import datetime
import jwt
import logging

def timestamp(from_datetime):
  return timegm(from_datetime.utctimetuple())

def _salt_generator(claims):
  """Generate a secret for the JOAT.

  You need to implement this method in order to use the generator.

  The JWT claims are passed into the generator so that you can access the
  claims fields to generate the HMAC salt.  This is useful if you need the user
  id to look up the salt in a database, or if you combine the other fields with
  a secret to generate the salt.
  """
  logging.debug("salt_generator is not implemented!")
  raise NotImplementedError

salt_generator = _salt_generator

def parse_token(token):
  """Parses a JWT OAuth 2.0 Access Token into a joat.Token object.

  Raises an ExpiredSignature exception if the token is expired.
  Returns None in other cases of invalidity."""

  try:
    claims, enc, header, sig = jwt.load(token)
    salt = salt_generator(claims)
    verified_claims = jwt.decode(token, salt)
  except jwt.DecodeError as e:
    # improperly formatted token
    return None
  except jwt.ExpiredSignature as e:
    # token is expired, return none
    return None

  payload = {
    'provider': verified_claims['iss'],
    'client_id': verified_claims['aud'],
    'user_id': verified_claims['sub'],
    'authorized_scope': verified_claims['scp']
  }

  if 'jti' in verified_claims:
    payload['jti'] = verified_claims['jti']

  return payload

class TokenGenerator(object):
  """A class that generates JWT OAuth 2.0 Access Tokens.

  Each instance of TokenGenerator is necessarily tied to a provider, and
  may also be tied to a user and/or an OAuth client.
  """

  provider_name = None
  client_id = None
  user_id = None
  scope = None
  default_lifetime = datetime.timedelta(hours=1)

  def __init__(self, name, client_id=None):
    self.provider_name = name
    self.client_id = client_id
    if salt_generator == _salt_generator:
      raise NotImplementedError("You must set the JOAT salt generator before initializing a TokenGenerator")

  def issue_token(self, **kwargs):
    """Issue an access token to the client for the user and scope provided."""

    now = datetime.datetime.utcnow()

    # Use the class properties for anything not passed in
    provider = kwargs.get('provider', self.provider_name)
    client_id = kwargs.get('client_id', self.client_id)
    user_id = kwargs.get('user_id', self.user_id)
    scope = kwargs.get('scope', self.scope)
    issued_at = kwargs.get('issued_at', now)
    lifetime = kwargs.get('lifetime', self.default_lifetime)
    jti = kwargs.get('jti', None)

    # Make sure everything is present
    if provider is None:
      raise TypeError("Cannot issue a JOAT without a provider name")

    if client_id is None:
      raise TypeError("Cannot issue a JOAT without a client_id")

    if user_id is None:
      raise TypeError("Cannot issue a JOAT without a user_id")

    if scope is None or not isinstance(scope, list):
      raise TypeError("Invalid scope.  Must be a list of permissions, and cannot be None.")

    if issued_at is None or not isinstance(issued_at, datetime.datetime):
      raise TypeError("Invalid issued_at.  Token must be issued at some datetime.datetime.")

    if lifetime is None or not isinstance(lifetime, datetime.timedelta):
      raise TypeError("Invalid JOAT lifetime.  Lifetime must be datetime.timedelta")

    # Populate the claims
    expires = issued_at + lifetime

    claims = {
      'iss': provider,
      'aud': client_id,
      'sub': user_id,
      'scp': scope,
      'iat': timegm(issued_at.utctimetuple()),
      'exp': timegm(expires.utctimetuple())
    }

    if jti is not None:
      claims['jti'] = jti

    # And generate the token
    secret = salt_generator(claims)
    token = jwt.encode(claims, secret)
    return token
