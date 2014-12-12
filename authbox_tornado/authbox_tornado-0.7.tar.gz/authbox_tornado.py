import hashlib
import json
import logging
import random
import time
import tornado.concurrent
import tornado.escape
import tornado.httpclient
import traceback
import uuid

AUTHBOX_CONFIG = {
  'api_key': None,
  'connect_timeout': 500,
  'enable_tracking_pixel': True,
  'endpoint': 'https://api.authbox.io/api',
  'logging_level': logging.ERROR,
  'get_request_data': lambda req, **kwargs: {},
  'request_timeout': 500,
  'secret_key': None,
}

AUTHBOX_LOGGER = logging.getLogger('authbox')

AUTHBOX_END_BODY_TAG = '</body>'
AUTHBOX_END_HTML_TAG = '</html>'
AUTHBOX_PIXEL_LIKELIHOOD = .01 # 1% of requests get the pixel even if it's not needed for certain.
AUTHBOX_PIXEL_TEMPLATE = '<iframe src="%s/pixel?LMID=%s" width="0" height="0" style="border: none" />'

AUTHBOX_HTTP_CLIENT = tornado.httpclient.AsyncHTTPClient()

current_milli_time = lambda: int(round(time.time() * 1000))

# ordered by priority; earlier ones override later ones.
AUTHBOX_IP_HEADERS = ['cf-connecting-ip', 'cf-remote-addr', 'x-forwarded-for']

def authbox_configure(config_updates):
  AUTHBOX_CONFIG.update(config_updates)
  AUTHBOX_LOGGER.setLevel(AUTHBOX_CONFIG['logging_level'])


def authbox_get_unique_id():
  return hashlib.sha256(str(uuid.uuid1())).hexdigest()


def authbox_get_cookie(cookie_type):
  return hashlib.sha256(':'.join(['authbox', cookie_type, AUTHBOX_CONFIG['api_key']])).hexdigest()


def authbox(request_handler_class):
  '''Takes a Tornado RequestHandler class and adds support for Authbox'''
  class NewRequestHandler(request_handler_class):
    __name__ = request_handler_class.__name__
    def __init__(self, *args, **kwargs):
      request_handler_class.__init__(self, *args, **kwargs)
      self._authbox_verdict = None
      self._authbox_insert_pixel = random.random() < AUTHBOX_PIXEL_LIKELIHOOD

      self._authbox_local_machine_id = self.get_cookie(authbox_get_cookie('local_machine_id'))
      self._authbox_new_local_machine_id = False
      self._authbox_pixel_inserted = False
      self._authbox_fired = {
        'log': False,
        'check': False
      }
      self._authbox_check_action = None

      if self._authbox_local_machine_id is None:
        # When creating a new cookie we must perform the linking operation.
        self._authbox_insert_pixel = True
        self._authbox_local_machine_id = authbox_get_unique_id()
        self._authbox_new_local_machine_id = True

      if self.get_cookie(authbox_get_cookie('did_get_pixel')) is None:
        self._authbox_insert_pixel = True

      self.set_cookie(
        authbox_get_cookie('local_machine_id'),
        self._authbox_local_machine_id,
        expires_days=365*2
      )

      self._authbox_pixel_markup = AUTHBOX_PIXEL_TEMPLATE % (AUTHBOX_CONFIG['endpoint'], self._authbox_local_machine_id)

    def _get_request_body(self, action, request_data):
      if request_data is None:
        request_data = {}

      remote_ip = self.request.remote_ip
      for remote_ip_header in AUTHBOX_IP_HEADERS:
        if remote_ip_header in self.request.headers:
          remote_ip = self.request.headers[remote_ip_header].split(',')[0]
          break

      action.update({
        '$apiKey': AUTHBOX_CONFIG['api_key'],
        '$secretKey': AUTHBOX_CONFIG['secret_key'],
        '$localMachineID': {
          '$key': self._authbox_local_machine_id,
          '$new': self._authbox_new_local_machine_id
        },
        '$ipAddress': remote_ip,
        '$userAgent': self.request.headers.get('user-agent'),
        '$host': self.request.headers.get('host'),
        '$referer': self.request.headers.get('referer'),
        '$timestamp': current_milli_time(),
        '$endpointURL': self.request.full_url(),
      })
      action.update(request_data)
      return action

    @tornado.gen.coroutine
    def _authbox_check(self, endpoint, action=None):
      if action is None:
        action = {}

      try:
        request_data = yield tornado.gen.maybe_future((AUTHBOX_CONFIG['get_request_data'])(self))
        request = self._get_request_body(action, request_data)
        json_request = tornado.escape.json_encode(request)
        AUTHBOX_LOGGER.info('Sending JSON: ' + json_request)
        result = yield AUTHBOX_HTTP_CLIENT.fetch(
          AUTHBOX_CONFIG['endpoint'] + endpoint,
          method='POST',
          connect_timeout=AUTHBOX_CONFIG['connect_timeout'],
          request_timeout=AUTHBOX_CONFIG['request_timeout'],
          headers={'Content-Type': 'application/json; charset=UTF-8'},
          body=json_request,
        )
        if not result or result.code != 200 or not result.buffer:
          AUTHBOX_LOGGER.warning('Request was not successful')
          self._authbox_verdict = {'type': 'ALLOW', 'info': 'Error from server.'}
        else:
          self._authbox_verdict = json.loads(result.buffer.read())
      except Exception, e:
        tb = traceback.format_exc()
        AUTHBOX_LOGGER.warning('Error occurred when sending check to Authbox: %s' % tb)
        self._authbox_verdict = {'type': 'ALLOW', 'info': 'Error: %s' % e}
      raise tornado.gen.Return(self._authbox_verdict)

    def _authbox_ensure_one_action(self, type):
      if self._authbox_fired[type]:
        AUTHBOX_LOGGER.warning('You can only fire one action per http request.')
        return False

      self._authbox_fired[type] = True
      return True

    def authbox_check(self, action=None):
      '''Sends AuthboxAction event to AuthboxServer. A verdict is returned.

      It is up to the user if they want to honor the Verdict or just want to log
      the actions into AuthboxServers.
      Args:
        action: Dict containing action information.
      Returns:
        Future of type Verdict: {type: (ALLOW|BLOCK|etc), info: (optional additional info)}
      '''
      if not self._authbox_ensure_one_action('check'):
        future = tornado.concurrent.Future()
        future.set_result(self._authbox_verdict)
        return future

      self._authbox_check_action = action
      return self._authbox_check('/action_check', action)

    def authbox_log(self, action=None):
      if not self._authbox_ensure_one_action('log'):
        return

      if self._authbox_fired['check'] and self._authbox_verdict['type'] != 'ALLOW':
        return

      self._authbox_check('/action_log', action)

    def write(self, chunk):
      request_handler_class.write(self, chunk)

      content_type = self._headers.get('content-type', '').lower()
      if ('text/html' not in content_type and
          'text/xhtml' not in content_type):
        # not an html response
        return

      if (self._authbox_pixel_inserted or
          not self._authbox_insert_pixel or
          not AUTHBOX_CONFIG['enable_tracking_pixel']):
        return

      chunk = b''.join(self._write_buffer)
      if AUTHBOX_END_BODY_TAG in chunk:
        chunk = chunk.replace(
          AUTHBOX_END_BODY_TAG,
          '%s%s' % (self._authbox_pixel_markup, AUTHBOX_END_BODY_TAG)
        )
        self._authbox_pixel_inserted = True
      elif AUTHBOX_END_HTML_TAG in chunk:
        chunk = chunk.replace(
          AUTHBOX_END_HTML_TAG,
          '%s%s' % (self._authbox_pixel_markup, AUTHBOX_END_HTML_TAG)
        )
        self._authbox_pixel_inserted = True

      self._write_buffer = [chunk]

      if self._authbox_pixel_inserted:
        self.set_cookie(
          authbox_get_cookie('did_get_pixel'),
          '1',
          expires_days=365*2
        )

    def on_finish(self):
      if not self._authbox_fired['log']:
        # Send a generic action and ignore the results
        self.authbox_log(self._authbox_check_action)
      request_handler_class.on_finish(self)

  return NewRequestHandler

__all__ = ['authbox', 'authbox_configure']
