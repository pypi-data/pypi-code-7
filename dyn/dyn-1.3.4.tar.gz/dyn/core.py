# -*- coding: utf-8 -*-
"""dyn.core is a utilities module for use internally within the dyn library
itself. Although it's possible to use this functionality outside of the dyn
library, it is not recommened and could possibly result in some strange
behavior.
"""
import copy
import time
import locale
import logging
import threading
from datetime import datetime
from collections import OrderedDict

from . import __version__
from .compat import (HTTPConnection, HTTPSConnection, HTTPException, json,
                     prepare_to_send, force_unicode, string_types)


def cleared_class_dict(dict_obj):
    """Return a cleared dict of class attributes. The items cleared are any
    fields which evaluate to None, and any methods
    """
    return {x: dict_obj[x] for x in dict_obj if dict_obj[x] is not None and
            not hasattr(dict_obj[x], '__call__')}


def clean_args(dict_obj):
    """Clean a dictionary of API arguments to prevent the display of plain text
    passwords to users

    :param dict_obj: The dictionary of arguments to be cleaned
    """
    cleaned_args = copy.deepcopy(dict_obj)
    if 'password' in cleaned_args:
        cleaned_args['password'] = '*****'
    return cleaned_args


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        cur_thread = threading.current_thread()
        key = getattr(cls, '__metakey__')
        if key not in cls._instances:
            cls._instances[key] = {
                # super(Singleton, cls) evaluates to type; *args/**kwargs get
                # passed to class __init__ method via type.__call__
                cur_thread: super(_Singleton, cls).__call__(*args, **kwargs)
            }
        elif key in cls._instances and cur_thread not in cls._instances[key]:
            cls._instances[key][cur_thread] = \
                super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[key][cur_thread]


# This class is a workaround for supporting metaclasses in both Python2 and 3
class Singleton(_Singleton('SingletonMeta', (object,), {})):
    """A :class:`~dyn.core.Singleton` type for implementing a true Singleton
    design pattern, cleanly, using metaclasses
    """
    pass


class APIDescriptor(object):
    def __init__(self, name='', doc=None):
        super(APIDescriptor, self).__init__()
        self.name = name
        self.private_name = '_' + self.name
        self.__doc__ = doc

    def __get__(self, instance, cls):
        print('GET', instance, cls)
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        print('SET', instance, value)
        setattr(instance, self.private_name, value)
        if hasattr(instance, '_update'):
            args = {self.name: value}
            getattr(instance, '_update')(args)


class Typed(APIDescriptor):
    """Type enforced descriptor"""
    ty = object

    def __set__(self, instance, value):
        if not isinstance(value, self.ty):
            raise TypeError('Expected %s' % self.ty)
        super(Typed, self).__set__(instance, value)


class IntegerField(Typed):
    """API Field that may only be an integer type"""
    ty = int


class StringField(Typed):
    """API Field that may only be a string type"""
    ty = string_types


class ImmutableField(APIDescriptor):
    """An API field that can not be overridden"""

    def __set__(self, instance, cls):
        pass


class ValidatedField(APIDescriptor):
    """An API field whose value can be forced to a specific subset of values"""
    def __init__(self, name='', doc=None, validator=None):
        """An API field that must be one of a specific set of values

        :param name: The name of this field
        :param validator: An optional list of valid values for this field
        """
        super(ValidatedField, self).__init__(name, doc)
        self.validator = validator

    def __set__(self, instance, value):
        if self.validator is not None:
            if value in self.validator:
                super(ValidatedField, self).__set__(instance, value)
        else:  # If we have no validator, then assume it's safe to overwrite
            super(ValidatedField, self).__set__(instance, value)


# class Junk(object):
#     data = APIDescriptor('data')
#     odds = ValidatedField('odds', validator=[1, 3, 5, 7])
#     read_only = ImmutableField('read_only')
#     my_int = IntegerField('my_int')
#     my_str = StringField('my_str')
#
#     def __init__(self):
#         self._data = {'serial': 121312, 'ts': 12321111233}
#         self._odds = 5
#         self._read_only = 'passw0rd'
#         self._my_int = 0
#         self._my_str = 'lulz'


# noinspection PyUnusedLocal
class APIObject(object):
    """Base API Object type responsible for handling shared functionality
    between various objects constructed from what comes out of the API. This
    base object has some safe default behavior such as a _build method that
    simply takes in api data and appends a '_' to the name before assigning it
    as a variable for the instance. A _get method that passes no arguments to
    the API. And a delete that passes no arguments to the API.

    This class also provides a __json__ attribute that attempts to generify
    the conversion of these Python objects into JSON blobs. By default this
    property creates a cleared_class_dict and further filters out any instance
    attributes that start with '_' but not '__'.
    """
    uri = ''
    session_type = None

    def __init__(self, *args, **kwargs):
        super(APIObject, self).__init__()
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:  # Safe default behaviour
            self._get()
        else:
            self._post(*args, **kwargs)

    def _build(self, data):
        """Build the variables in this object by pulling out the data from the
        provided data dict
        """
        for key, val in data.items():
            setattr(self, '_' + key, val)

    def _post(self, *args, **kwargs):
        """POST method, to be inherited by all child classes on a case-by-case
        basis
        """
        raise NotImplementedError('_post must be overriden by child classes')

    def _get(self, *args, **kwargs):
        """Retrieve this object from the DynECT System"""
        response = self.session_type.get_session().execute(self.uri, 'GET')
        self._build(response['data'])

    def _update(self, **api_args):
        """Update this object on the DynECT System"""
        response = self.session_type.get_session().execute(self.uri, 'PUT',
                                                           api_args)
        self._build(response['data'])

    def delete(self, *args, **kwargs):
        """Delete this object from the DynECT system"""
        if self.session_type is not None:
            self.session_type.get_session().execute(self.uri, 'DELETE')

    @property
    def __json__(self):
        """Generic JSON reprsentation of this object"""
        dict_obj = cleared_class_dict(self.__dict__)
        return {x: dict_obj[x] for x in dict_obj if x.startswith('_') and
                not x.startswith('__')}


class _History(list):
    """A *list* subclass specifically targeted at being able to store the
    history of calls made via a SessionEngine
    """

    def append(self, p_object):
        """Override builtin list append operators to allow for the automatic
        appendation of a timestamp for cleaner record keeping
        """
        now_ts = datetime.now().isoformat()
        super(_History, self).append(tuple([now_ts] + list(p_object)))


# noinspection PyMethodParameters
class SessionEngine(Singleton):
    """Base object representing a DynectSession Session"""
    _valid_methods = tuple()
    uri_root = '/'

    def __init__(self, host=None, port=443, ssl=True, history=False):
        """Initialize a Dynect Rest Session object and store the provided
        credentials

        :param host: DynECT API server address
        :param port: Port to connect to DynECT API server
        :param ssl: Enable SSL
        :param history: A boolean flag determining whether or not you would
            like to store a record of all API calls made to review later
        :return: SessionEngine object
        """
        super(SessionEngine, self).__init__()
        self.__call_cache = _History() if history else None
        self.extra_headers = dict()
        self.logger = logging.getLogger(self.name)
        self.host = host
        self.port = port
        self.ssl = ssl
        self.poll_incomplete = True
        self.content_type = 'application/json'
        self._encoding = locale.getdefaultlocale()[-1] or 'UTF-8'
        self._token = self._conn = self._last_response = None
        self._permissions = None

    @classmethod
    def new_session(cls, *args, **kwargs):
        """Return a new session instance, regardless of whether or not there is
        already an existing session.

        :param args: Arguments to be passed to the Singleton __call__ method
        :param kwargs: keyword arguments to be passed to the Singleton __call__
            method
        """
        cur_thread = threading.current_thread()
        key = getattr(cls, '__metakey__')
        instance = cls._instances.get(key, {}).get(cur_thread, None)
        if instance:
            instance.close_session()
        return cls.__call__(*args, **kwargs)

    @classmethod
    def get_session(cls):
        """Return the current session for this Session type or None if there is
        not an active session
        """
        cur_thread = threading.current_thread()
        key = getattr(cls, '__metakey__')
        return cls._instances.get(key, {}).get(cur_thread, None)

    @classmethod
    def close_session(cls):
        """Remove the current session from the dict of instances and return it.
        If there was not currently a session being stored, return None. If,
        after removing this session, there is nothing under the current key,
        delete that key's entry in the _instances dict.
        """
        cur_thread = threading.current_thread()
        key = getattr(cls, '__metakey__')
        closed = cls._instances.get(key, {}).pop(cur_thread, None)
        if len(cls._instances.get(key, {})) == 0:
            cls._instances.pop(key, None)
        return closed

    @property
    def name(self):
        """A human readable version of the name of this object"""
        return str(self.__class__).split('.')[-1][:-2]

    def connect(self):
        """Establishes a connection to the REST API server as defined by the
        host, port and ssl instance variables
        """
        if self._token:
            self.logger.debug('Forcing logout from old session')
            orig_value = self.poll_incomplete
            self.poll_incomplete = False
            self.execute('/REST/Session', 'DELETE')
            self.poll_incomplete = orig_value
            self._token = None
        self._conn = None
        if self.ssl:
            msg = 'Establishing SSL connection to {}:{}'.format(self.host,
                                                                self.port)
            self.logger.info(msg)
            self._conn = HTTPSConnection(self.host, self.port, timeout=300)
        else:
            msg = 'Establishing unencrypted connection to {}:{}'
            msg = msg.format(self.host, self.port)
            self.logger.info(msg)
            self._conn = HTTPConnection(self.host, self.port, timeout=300)

    def _process_response(self, response, method, final=False):
        """API Method. Process an API response for failure, incomplete, or
        success and throw any appropriate errors

        :param response: the JSON response from the request being processed
        :param method: the HTTP method
        :param final: boolean flag representing whether or not to continue
            polling
        """
        return response

    def _handle_error(self, uri, method, raw_args):
        """Handle the processing of a connection error with the api. Note, to
        be implemented as needed in subclasses.
        """
        return None

    def _handle_response(self, response, uri, method, raw_args, final):
        """Handle the processing of the API's response"""
        body = response.read()
        self._last_response = response

        if self.poll_incomplete:
            response, body = self.poll_response(response, body)
            self._last_response = response
        ret_val = json.loads(body.decode('UTF-8'))
        if self.__call_cache is not None:
            self.__call_cache.append((uri, method, clean_args(raw_args),
                                      ret_val['status']))

        self._meta_update(uri, method, ret_val)
        # Handle retrying if ZoneProp is blocking the current task
        error_msg = 'Operation blocked by current task'
        if ret_val['status'] == 'failure' and error_msg in \
                ret_val['msgs'][0]['INFO'] and not final:
            time.sleep(8)
            return self.execute(uri, method, raw_args, final=True)
        else:
            return self._process_response(ret_val, method)

    def _validate_uri(self, uri):
        """Validate and return a cleaned up uri. Make sure the command is
        prefixed by '/REST/'
        """
        if not uri.startswith('/'):
            uri = '/' + uri

        if not uri.startswith(self.uri_root):
            uri = self.uri_root + uri

        return uri

    def _validate_method(self, method):
        """Validate the provided HTTP method type"""
        if method.upper() not in self._valid_methods:
            msg = '{} is not a valid HTTP method. Please use one of {}'
            msg = msg.format(method, ', '.join(self._valid_methods))
            raise ValueError(msg)

    def _prepare_arguments(self, args, method, uri):
        """Prepare the arguments to be sent off to the API"""
        if args is None:
            args = {}
        if not isinstance(args, dict):
            # If args is an object type, parse it's dict for valid args
            # If an item in args.__dict__ has a _json attribute, use that in
            # place of the actual object
            d = args.__dict__
            args = {(x if not x.startswith('_') else x[1:]):
                    (d[x] if not hasattr(d[x], '_json') else getattr(d[x],
                                                                     '_json'))
                    for x in d if d[x] is not None and
                    not hasattr(d[x], '__call__') and x.startswith('_')}
        return args, json.dumps(args), uri

    def execute(self, uri, method, args=None, final=False):
        """Execute a commands against the rest server

        :param uri: The uri of the resource to access. /REST/ will be prepended
            if it is not at the beginning of the uri
        :param method: One of 'DELETE', 'GET', 'POST', or 'PUT'
        :param args: Any arguments to be sent as a part of the request
        :param final: boolean flag representing whether or not we have already
            failed executing once or not
        """
        if self._conn is None:
            self.connect()

        uri = self._validate_uri(uri)

        # Make sure the method is valid
        self._validate_method(method)

        # Prepare arguments to send to API
        raw_args, args, uri = self._prepare_arguments(args, method, uri)

        msg = 'uri: {}, method: {}, args: {}'
        self.logger.debug(msg.format(uri, method,
                                     clean_args(json.loads(args))))

        # Send the command and deal with results
        self.send_command(uri, method, args)

        # Deal with the results
        try:
            response = self._conn.getresponse()
        except (IOError, HTTPException) as e:
            if final:
                raise e
            else:
                # Handle processing a connection error
                resp = self._handle_error(uri, method, raw_args)
                # If we got a valid response back from our _handle_error call
                # Then return it, otherwise raise the original exception
                if resp is not None:
                    return resp
                raise e

        return self._handle_response(response, uri, method, raw_args, final)

    def _meta_update(self, uri, method, results):
        """Update the HTTP session token if the uri is a login or logout

        :param uri: the uri from the call being updated
        :param method: the api method
        :param results: the JSON results
        """
        # If we had a successful log in, update the token
        if uri.startswith('/REST/Session') and method == 'POST':
            if results['status'] == 'success':
                self._token = results['data']['token']

        # Otherwise, if it's a successful logout, blank the token
        if uri.startswith('/REST/Session') and method == 'DELETE':
            if results['status'] == 'success':
                self._token = None

    def poll_response(self, response, body):
        """Looks at a response from a REST command, and while indicates that
        the job is incomplete, poll for response

        :param response: the JSON response containing return codes
        :param body: the body of the HTTP response
        """
        while response.status == 307:
            time.sleep(1)
            uri = response.getheader('Location')
            self.logger.info('Polling {}'.format(uri))

            self.send_command(uri, 'GET', '')
            response = self._conn.getresponse()
            body = response.read()
        return response, body

    def send_command(self, uri, method, args):
        """Responsible for packaging up the API request and sending it to the
        server over the established connection

        :param uri: The uri of the resource to interact with
        :param method: The HTTP method to use
        :param args: Encoded arguments to send to the server
        """
        self._conn.putrequest(method, uri)

        # Build headers
        user_agent = 'dyn-py v{}'.format(__version__)
        headers = {'Content-Type': self.content_type, 'User-Agent': user_agent}
        for key, val in self.extra_headers.items():
            headers[key] = val

        if self._token is not None:
            headers['Auth-Token'] = self._token

        for key, val in headers.items():
            self._conn.putheader(key, val)

        # Now the arguments
        self._conn.putheader('Content-length', '%d' % len(args))
        self._conn.endheaders()

        self._conn.send(prepare_to_send(args))

    def wait_for_job_to_complete(self, job_id, timeout=120):
        """When a response comes back with a status of "incomplete" we need to
        wait and poll for the status of that job until it comes back with
        success or failure

        :param job_id: the id of the job to poll for a response from
        :param timeout: how long (in seconds) we should wait for a valid
            response before giving up on this request
        """
        self.logger.debug('Polling for job_id: {}'.format(job_id))
        start = datetime.now()
        uri = '/Job/{}/'.format(job_id)
        api_args = {}
        # response = self.execute(uri, 'GET', api_args)
        response = {'status': 'incomplete'}
        now = datetime.now()
        self.logger.warn('Waiting for job {}'.format(job_id))
        too_long = (now - start).seconds < timeout
        while response['status'] is 'incomplete' and too_long:
            time.sleep(10)
            response = self.execute(uri, 'GET', api_args)
        return response

    def __getstate__(cls):
        """Because HTTP/HTTPS connections are not serializeable, we need to
        strip the connection instance out before we ship the pickled data
        """
        d = cls.__dict__.copy()
        d.pop('_conn')
        return d

    def __setstate__(cls, state):
        """Because the HTTP/HTTPS connection was stripped out in __getstate__
        we must manually re-enter it as None and let the sessions execute
        method handle rebuilding it later
        """
        cls.__dict__ = state
        cls.__dict__['_conn'] = None

    def __str__(self):
        """str override"""
        return force_unicode('<{}>').format(self.name)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())

    @property
    def history(self):
        """A history of all API calls that have been made during the duration
        of this Session's existence. These API call details are returned as a
        *list* of 5-tuples of the form: (timestamp, uri, method, args, status)
        where status will be one of 'success' or 'failure'
        """
        return self.__call_cache
