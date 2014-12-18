import json
import logging

from webtest import TestApp

import squirro.common.config
from common import DummyUserProxy, MultiAppRequestWrapper, setup_session, \
    setup_session_user_objects
from squirro.common.dependency import get_injected, register_instance
from squirro.common.testing import AppRequestWrapper, setup_producer, \
    TestCaseMixin
from squirro.lib.configuration.testing import setup_config_client
from squirro.lib.topic_proxy import TopicAPIProxy
from squirro_client.base import SquirroClient
from squirro_client.exceptions import ClientError

log = logging.getLogger(__name__)

# register configuration and helper methods
config = squirro.common.config.get_test_config('squirro.api.bulk')
config.add_section('user')
config.set('user', 'pw_salt', 'salt')
config.add_section('topic_proxy')
config.set('topic_proxy', 'get_source_expiry_days', '1')
config.set('topic_proxy', 'get_project_expiry_days', '1')
register_instance('config', config)

register_instance('source_preview_cache', None)
register_instance('provider_preview_cache', None)

# import the model and application after everything has been setup
from squirro.api.bulk.background import TaskProcessor
from squirro.api.bulk.main import app as app_bulk
from squirro.api.topic.main import app as app_topic
from squirro.api.user.main import app as app_user
from squirro.service.topic_proxy.main import app as app_topic_proxy


class TestBulkApiMixin(TestCaseMixin):
    """Make sure the Squirro client bulk API mixin works as expected."""

    def setUp(self):
        register_instance('config', config)
        register_instance('source_preview_cache', None)
        register_instance('provider_preview_cache', None)
        register_instance('node_id', 'node.domain.com')

        # register dependencies
        setup_session()
        setup_session_user_objects()
        setup_config_client(value=None)

        # create a new application wrapper which also answers the token
        # refresh requests
        wrapper = MultiAppRequestWrapper({
            config.get('services', 'bulk'): AppRequestWrapper(TestApp(app_bulk)),
            config.get('services', 'user'): AppRequestWrapper(TestApp(app_user)),
            config.get('services', 'topic'): AppRequestWrapper(TestApp(app_topic)),
            config.get('services', 'topic_proxy'): AppRequestWrapper(TestApp(app_topic_proxy)),
        })
        register_instance('requests', wrapper)
        register_instance('requests_module', wrapper)

        register_instance('fingerprint_client', None)
        register_instance('user_proxy', DummyUserProxy())

        # and a producer
        self.producer_remote = setup_producer('producer_remote')
        self.producer_local = setup_producer('producer_local')

        # create new client
        self.client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests_module'),
            user_api_url=config.get('services', 'user'),
            topic_api_url=config.get('services', 'topic'),
            bulk_api_url=config.get('services', 'bulk'))
        self.client.access_token = 'token01'
        self.client.refresh_token = 'token02'

        # create a topic_proxy
        register_instance('topic_proxy', TopicAPIProxy())

    def test_new_shim(self):
        """Make sure that new shims can be registered."""

        config = {
            'ext': {'user_id': '005E0000001NSP0IAO'},
            'name': 'Salesforce Integration Shim', 'type': 'my-shim-type',
            'squirro': {
                'project': 'Accounts',
            }
        }

        ret = self.client.new_shim(config)
        self.assertNotEqual(ret.get('id'), None)

        # store shim id for future use
        self.shim_id = ret.get('id')

    def test_new_job(self):
        """Make sure that new jobs can be created."""
        self.test_new_shim()

        res = self.client.new_shim_job(self.shim_id)
        self.assertNotEqual(res.get('id'), None)

        # store job id for future use
        self.job_id = res.get('id')

    def test_new_shim_invalid_config(self):
        """Make sure that invalid shim configurations are reported as such by
        the bulk API.
        """

        config = {}
        invalid = False
        try:
            self.client.new_shim(config)
        except ClientError as ex:
            self.assertEqual(len(ex.data.get('errors')), 2)
            invalid = True
        self.assertEqual(invalid, True)

    def test_get_user_shims(self):
        """Make sure that shims can be retrieved by parameters."""

        # register shim
        self.test_new_shim()

        # retrieve shim by type
        ret = self.client.get_user_shims(type='my-shim-type')
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['id'], self.shim_id)
        self.assertEqual(ret[0]['type'], 'my-shim-type')

    def test_get_user_shims_no_type(self):
        """Make sure that shims can be retrieved without parameters."""
        # register shim
        self.test_new_shim()

        # retrieve shim without type
        ret = self.client.get_user_shims()
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]['id'], self.shim_id)
        self.assertEqual(ret[0]['type'], 'my-shim-type')

    def test_new_shim_objects(self):
        """Make sure that objects can be processed."""

        # register shim and job
        self.test_new_job()

        # objects test cases
        objects = [
            ([], {'delete': 0, 'errors': [], 'total': 0, 'error': 0,
                  'insert': 0, 'update': 0}),
            ([{'id': 'myid', 'name': 'My Name'}],
             {'delete': 0,
              'error': 1,
              'errors': [{'errors': ['mandatory attribute "type" missing',
                                     'mandatory attribute "project" missing',
                                     'attribute signals requires a mapping type',
                                     'invalid project "None" for object "myid"'],
                          'index': 0}],
             'total': 1,
             'insert': 0, 'update': 0}),
            ([{'id': 'lex@squirro.com', 'name': 'Alexander Sennhauser',
               'type': 'contact', 'project': 'Accounts',
               'signals': {
                   'emails': ['lex@squirro.com', 'info@squirro.com'],
                   'urls': ['http://squirro.com'],
                   'firstname': 'Alexander', 'lastname': 'Sennhauser',
                   'city': u'Z\xfcrich', 'country': 'Switzerland'}}],
             {'delete': 0, 'errors': [], 'total': 1, 'error': 0, 'insert': 1,
              'update': 0}),
        ]

        for objs, expected in objects:
            ret = self.client.new_shim_objects(self.shim_id, self.job_id, objs)
            self.assertEqual(ret, expected)

    def test_new_shim_object(self):
        """Make sure that a single object can be processed."""

        # register shim and job
        self.test_new_job()

        # single object test cases
        objects = [
            ({}, {'delete': 0, 'errors': [], 'total': 0, 'error': 0,
                  'insert': 0, 'update': 0, 'object_id': None,
                  'squirro_object_id': None}),
            ({'id': 'myid', 'name': 'My Name'},
             {'delete': 0,
              'error': 1,
              'errors': [{'errors': ['mandatory attribute "type" missing',
                                     'mandatory attribute "project" missing',
                                     'attribute signals requires a mapping type',
                                     'invalid project "None" for object "myid"'],
                          'index': 0}],
             'total': 1,
             'insert': 0, 'update': 0, 'object_id': None, 'squirro_object_id': None}),
            ({'id': 'lex@squirro.com', 'name': 'Alexander Sennhauser',
              'type': 'contact', 'project': 'Accounts',
              'signals': {
                  'emails': ['lex@squirro.com', 'info@squirro.com'],
                  'urls': ['http://squirro.com'],
                  'firstname': 'Alexander', 'lastname': 'Sennhauser',
                  'city': u'Z\xfcrich', 'country': 'Switzerland'}},
             {'delete': 0, 'errors': [], 'total': 1, 'error': 0, 'insert': 1,
              'update': 0, 'object_id': 'to-be-completed',
              'squirro_object_id': 'to-be-completed'}),
        ]
        for obj, expected in objects:
            ret = self.client.new_shim_object(self.shim_id, self.job_id, obj)

            # extract the object and squirro_object id if it is really defined
            if ret.get('object_id'):
                expected['object_id'] = ret['object_id']
                self.object_id = ret['object_id']
            if ret.get('squirro_object_id'):
                expected['squirro_object_id'] = ret['squirro_object_id']
                self.squirro_object_id = ret['squirro_object_id']
            self.assertEqual(ret, expected)

    def test_get_shim_objects(self):
        """Make sure that multiple objects can be retrieved from a project.
        """

        # register shim and create a single object
        self.test_new_job()
        self.test_new_shim_object()

        # Create a second test object
        obj = {
            'id': 'patrice@squirro.com', 'name': 'Patrice Neff',
            'type': 'contact', 'project': 'Accounts', 'signals': {},
        }
        ret = self.client.new_shim_object(self.shim_id, self.job_id, obj)
        assert not ret.get('errors'), repr(ret)
        object2_id = ret['object_id']
        squirro_object2_id = ret['squirro_object_id']

        ret = self.client.get_shim_objects(
            self.shim_id, ['lex@squirro.com', 'foo', 'patrice@squirro.com'])
        self.assertEqual(len(ret), 2)

        expected = {'id': self.object_id, 'squirro_object_id': self.squirro_object_id}
        self.assertEqual(ret[0], expected)

        expected = {'id': object2_id, 'squirro_object_id': squirro_object2_id}
        self.assertEqual(ret[1], expected)

    def test_get_project_objects(self):
        """Make sure that multiple objects can be retrieved and errors
        are silently ignored.
        """
        # register shim and create a single object
        self.test_new_job()
        self.test_new_shim_object()

        # Get the project ID which was created on shim creation
        projects = self.client.get_projects()
        assert len(projects) == 1
        account_project_id = projects[0]['id']

        # Create a second test object
        obj = {
            'id': 'patrice@squirro.com', 'name': 'Patrice Neff',
            'type': 'contact', 'project': 'Accounts', 'signals': {},
        }
        ret = self.client.new_shim_object(self.shim_id, self.job_id, obj)
        assert not ret.get('errors'), repr(ret)
        object2_id = ret['object_id']
        squirro_object2_id = ret['squirro_object_id']

        ret = self.client.get_project_objects(
            account_project_id, ['lex@squirro.com', 'foo', 'patrice@squirro.com'])
        self.assertEqual(len(ret), 2)

        expected = {'id': self.object_id, 'squirro_object_id': self.squirro_object_id}
        self.assertEqual(ret[0], expected)

        expected = {'id': object2_id, 'squirro_object_id': squirro_object2_id}
        self.assertEqual(ret[1], expected)

    def test_get_shim_object(self):
        """Make sure that single objects can be retrieved."""

        # register shim and create a single object
        self.test_new_job()
        self.test_new_shim_object()

        expected = {'id': self.object_id, 'squirro_object_id': self.squirro_object_id}
        ret = self.client.get_shim_object(self.shim_id, 'lex@squirro.com')
        self.assertEqual(ret, expected)

    def test_get_bulk_object_signals(self):
        """Make sure that squirro_object signals can be retrieved back from the bulk
        API.
        """

        # push new shim objects
        self.test_new_shim_objects()

        # process background tasks
        producer = get_injected('producer_remote')
        proc = TaskProcessor()
        for data, routing_key in producer._data:
            proc.on_task(data)

        # get the single squirro_object from the topic API
        projects = self.client.get_projects()
        squirro_objects = self.client.get_user_objects(projects[0]['id'])
        squirro_object = squirro_objects[0]

        # get the squirro_object signals with the default keys
        signals = self.client.get_bulk_object_signals(squirro_object['id'])
        urls = json.loads(signals.get('urls', '[]'))
        self.assertEqual(urls, ['http://squirro.com'])
        emails = json.loads(signals.get('emails', '[]'))
        self.assertEqual(emails, ['lex@squirro.com', 'info@squirro.com'])

        # also get some more signals by key
        signals = self.client.get_bulk_object_signals(
            squirro_object['id'], keys=['emails', 'firstname', 'city'])
        emails = json.loads(signals.get('emails', '[]'))
        self.assertEqual(emails, ['lex@squirro.com', 'info@squirro.com'])
        self.assertEqual(signals.get('firstname'), 'Alexander')
        self.assertEqual(signals.get('city'), u'Z\xfcrich')
