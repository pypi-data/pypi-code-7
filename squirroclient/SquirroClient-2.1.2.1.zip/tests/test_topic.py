import json
import os

from mox import IgnoreArg
from redis import StrictRedis
from webtest import TestApp, TestResponse

import squirro.common.config
from squirro.common.cache import MemoryCache
from squirro.common.dependency import get_injected, register_instance
from squirro.common.testing import AppRequestWrapper, AppResponseWrapper, \
    DummyResponse, RequestsTestCaseMixin, setup_producer, TestCaseMixin, \
    MoxTestCaseMixin
from squirro.lib.configuration.testing import setup_config_client
from squirro.lib.fingerprint import FingerprintClient
from squirro.lib.topic import Object, Project, Source, Subscription
from squirro_client.base import SquirroClient
from squirro_client.exceptions import NotFoundError, UnknownError

# register configuration and helper methods
config = squirro.common.config.get_test_config('squirro.api.topic')
register_instance('config', config)

# import the model and application after everything has been setup
from common import setup_session, DummyIndexReader, DummyUserProxy
from squirro.api.topic.main import app


class TopicAppRequestWrapper(AppRequestWrapper):
    """Application request wrapper which also intercepts the token refresh
    requests.
    """
    def post(self, *args, **kwargs):
        """Intercept POST requests."""

        url = args[0]
        if url.endswith('/oauth2/token'):
            return self._token_response()
        elif url.startswith('http://feed'):
            return self._feed_provider_response(url)
        else:
            return super(TopicAppRequestWrapper, self).post(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Intercept GET requests."""

        url = args[0]
        if url.startswith('http://feed'):
            return self._feed_provider_response(url)
        else:
            return super(TopicAppRequestWrapper, self).get(*args, **kwargs)

    def _token_response(self):
        """Prepare a token response."""

        data = {
            'access_token': 'token01', 'refresh_token': 'token02',
            'tenant': 'tenant01', 'user_id': 'user01',
            'permissions': ['admin'],
        }
        res = TestResponse(
            content_type='application/json', body=json.dumps(data))
        return AppResponseWrapper(res)

    def _feed_provider_response(self, url):
        """Prepare a feed provider response."""
        data = {
            'title': 'Squirro', 'link': 'http://blog.squirro.com',
            'config': {'url': 'http://blog.squirro.com/rss'}
        }
        res = TestResponse(
            content_type='application/json', body=json.dumps(data))
        return AppResponseWrapper(res)


class BaseTest(TestCaseMixin):
    def setUp(self):
        register_instance('config', config)

        # register dependencies
        setup_session()

        # create a new application wrapper which also answers the token
        # refresh requests
        wrapper = TopicAppRequestWrapper(TestApp(app))
        register_instance('requests', wrapper)
        register_instance('requests_module', wrapper)

        # setup config client
        setup_config_client(value=None)

        # register an index reader which returns a set of predefined set of
        # items
        register_instance(
            'index_reader', DummyIndexReader(self._setup_items_and_basedata()))

        # register a dummy fingerprint client
        register_instance('fingerprint_client', FingerprintClient())

        # register the user proxy
        register_instance('user_proxy', DummyUserProxy())

        # ID of the user which the client is accessing
        self.user_id = 'user01'

        # project identifier
        self.project_id = '2aEVClLRRA-vCCIvnuEAvQ'

        # a valid item identifier
        self.item_id = 'haG6fhr9RLCm7ZKz1Meouw'

        # create new client
        self.client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests_module'))
        self.client.access_token = 'token01'
        self.client.refresh_token = 'token02'

        # setup local and remote producer
        self.producer_remote = setup_producer('producer_remote')
        self.producer_local = setup_producer('producer_local')

        # setup lib.index caches
        register_instance('facet_fields_cache', MemoryCache())

    def _setup_items_and_basedata(self):
        """Create items which are returned by the index reader. Also creates
        the underlying datastructure of project, objects, sources and
        subscriptions."""

        # load items
        path = os.path.join(
            os.path.dirname(__file__), 'fixtures', 'items.json')
        raw = open(path, 'r').read()
        items = json.loads(raw)

        # create DB entries based on `items`
        sources = {}
        objects = {}
        subscriptions = {}
        projects = {}
        session = get_injected('session')
        for item in items:
            item['from_es'] = {}

            # add sources
            this_items_sources = []
            for source in item.get('sources', []):
                if not source['id'] in sources:
                    s = Source(id=source['id'], config='...',
                               link=source['link'], title=source['title'],
                               provider=source['provider'])
                    sources[s.id] = s
                    session.add(s)
                item['from_es'].setdefault('assoc:sources', [])\
                    .append(source['id'])
                this_items_sources.append(source['id'])

            # add projects/objects and subscriptions
            for object in item.get('objects'):
                if not object['id'] in objects:
                    if object['project_id'] not in projects:
                        f = Project(id=object['project_id'], owner_id='user01',
                                    tenant='tenant01')
                        projects[f.id] = f
                        session.add(f)
                    t = Object(id=object['id'],
                               project=projects[object['project_id']],
                               owner_id='user01')
                    objects[t.id] = t
                    session.add(t)
                for source_id in this_items_sources:
                    if not subscriptions.get((object['id'], source_id)):
                        sub = Subscription(object_id=object['id'],
                                           source_id=source_id)
                        subscriptions[(object['id'], source_id)] = sub
                        session.add(sub)

        # commit all changes
        session.commit()

        return items


class TestTopicAPIMixin(BaseTest, MoxTestCaseMixin):
    """Make sure the Squirro client object API mixin works as expected."""

    #
    # Items
    #

    def test_get_items(self):
        """Make sure that items for a user can be retrieved."""

        # get user items
        ret = self.client.get_items(self.project_id)
        self.assertEqual(ret['count'], 15)
        self.assertEqual(len(ret['items']), 15)

    def test_get_item(self):
        """Make sure that individual items can be retrieved."""

        # get individual item
        ret = self.client.get_item(self.project_id, self.item_id)
        self.assertEqual(ret['item']['id'], self.item_id)

    def test_get_item_notfound(self):
        """Make sure that the right exception is thrown if an item cannot be
        found.
        """

        # get item with unknown identifier
        self.assertRaises(
            NotFoundError, self.client.get_item, self.project_id, '123')

    def test_modify_item_star(self):
        """Make sure that individual items can be marked as starred."""
        pass

    def test_modify_item_read(self):
        """Make sure that individual items can be marked as read."""
        pass

    def test_delete_item(self):
        """Make sure that individual items can be deleted from the index."""
        pass

    def test_delete_item_deassociate(self):
        """Make sure that individual items can be de-associated from a list of
        object identifiers.
        """
        pass

    #
    # Folders
    #

    def test_new_project(self):
        """Make sure that projects can be created ok."""

        ret = self.client.new_project('My Folder')
        self.assertNotEqual(ret.get('id'), None)

        # store for future use
        self.project_id = ret['id']

        # read back the project and verify attributes
        ret = self.client.get_project(ret['id'])
        self.assertEqual(ret.get('id'), self.project_id)
        self.assertEqual(ret.get('title'), 'My Folder')

    def test_get_user_projects(self):
        """Make sure that we can retrieve user projects."""
        pass

    def test_get_user_projects_owner(self):
        """Make sure that we can retrieve user projects for a particular owner.
        """
        pass

    def test_get_user_projects_seeder(self):
        """Make sure that we can retrieve user projects for a particular
        seeder.
        """
        pass

    def test_get_user_projects_including_objects(self):
        """Make sure that we can retrieve user projects including objects."""
        pass

    def test_get_project(self):
        """Make sure that we can retrieve an individual project."""
        pass

    def test_modify_project_title(self):
        """Make sure that we can change the title of a project."""
        pass

    def test_delete_project(self):
        """Make sure that we can delete an individual project."""
        pass

    #
    # Topics
    #

    def test_get_user_object(self):
        """Make sure that user objects can be retrieved back."""
        pass

    def test_get_object(self):
        """Make sure that an individual object can be retrieved."""
        pass

    def test_new_object(self):
        """Make sure that objects are created with all expected attributes."""

        # create new project
        self.test_new_project()

        ret = self.client.new_object(
            self.project_id, 'My Topic', type='my type',
            is_ready=False)
        self.assertNotEqual(ret.get('id'), None)

        # store for future use
        self.object_id = ret['id']

        # read back the object and verify attributes
        ret = self.client.get_object(self.project_id, self.object_id)
        self.assertEqual(ret.get('id'), self.object_id)
        self.assertEqual(ret.get('project_id'), self.project_id)
        self.assertEqual(ret.get('title'), 'My Topic')
        self.assertEqual(ret.get('type'), 'my type')
        self.assertEqual(ret.get('is_ready'), False)

    def test_modify_object_change_projectid(self):
        """Make sure that the project id of a object can be changed."""
        pass

    def test_modify_object_change_title(self):
        """Make sure that the title of a object can be changed."""
        pass

    def test_modify_object_change_isready(self):
        """Make sure that a object can be marked as being ready."""
        pass

    def test_modify_object_change_override_managed_subscription(self):
        """Make sure that we can override the subscriptions for a object."""
        pass

    def test_modify_object_change_noiselevel(self):
        """Make sure that the noise level of a object can be changed."""
        pass

    def test_modify_object_change_query(self):
        """Make sure that the query of a object can be changed."""
        pass

    def test_delete_object(self):
        """Make sure that an individual object can be deleted."""
        pass

    #
    # Subscriptions
    #

    def test_new_subscription_user(self):
        """Make sure that we can create a new subscription which is not
        managed by a seeder, i.e. created by a user."""

        # create new object
        self.test_new_object()

        # create new subscription
        ret = self.client.new_subscription(
            self.project_id, self.object_id,
            'feed', {'url': 'http://blog.squirro.com/rss'})

        # store for future use
        self.user_subscription_id = ret['id']

        self.assertNotEqual(ret['id'], None)
        self.assertEqual(ret['deleted'], False)
        self.assertEqual(ret['seeder'], None)

    def test_new_subscription_seeder(self):
        """Make sure that we can create a new subscription which is managed by
        a seeder.
        """

        # create new object
        self.test_new_object()

        # create new subscription as a seeder
        ret = self.client.new_subscription(
            self.project_id, self.object_id, 'feed',
            {'url': 'http://blog.squirro.com/rss'},
            seeder='salesforce')

        # store for future use
        self.seeder_subscription_id = ret['id']

        self.assertNotEqual(ret['id'], None)
        self.assertEqual(ret['deleted'], False)

        self.assertEqual(ret['seeder'], 'salesforce')

    def test_delete_subscription_user_as_user(self):
        """Make sure that we can delete a user-managed subscription."""

        # mock cache interaction
        redis = self.mox.CreateMock(StrictRedis)
        redis.set(IgnoreArg(), '1')
        redis.keys(IgnoreArg())
        self.mox.ReplayAll()
        register_instance('redis_cache', redis)

        # create new user subscription
        self.test_new_subscription_user()

        # delete subscription
        self.client.delete_subscription(
            self.project_id, self.object_id, self.user_subscription_id)

        # subscription should be deleted
        self.assertRaises(
            NotFoundError, self.client.get_subscription,
            self.project_id, self.object_id, self.user_subscription_id)

    def test_delete_subscription_user_as_seeder(self):
        """Make sure that a user-managed subscription is not delted by a
        seeder.
        """

        # create new user subscription
        self.test_new_subscription_user()

        # delete subscription, this should be rejected
        try:
            self.client.delete_subscription(
                self.project_id, self.object_id, self.user_subscription_id,
                seeder='salesforce')
        except UnknownError as ex:
            self.assertEqual(ex.status_code, 403)

    def test_delete_subscription_seeder_as_user(self):
        """Make sure that we can delete a seeder-managed subscription as a
        user.
        """

        # create new seeder subscription
        self.test_new_subscription_seeder()

        # delete subscription, it should be marked as deleted
        self.client.delete_subscription(
            self.project_id, self.object_id, self.seeder_subscription_id)

        ret = self.client.get_subscription(
            self.project_id, self.object_id, self.seeder_subscription_id)

        self.assertEqual(ret['id'], self.seeder_subscription_id)
        self.assertEqual(ret['deleted'], True)
        self.assertEqual(ret['seeder'], 'salesforce')

    def test_delete_subscription_seeder_as_seeder(self):
        """Make sure that we can delete a seeder-managed subscription as a
        seeder.
        """

        # mock cache interaction
        redis = self.mox.CreateMock(StrictRedis)
        redis.set(IgnoreArg(), '1')
        redis.keys(IgnoreArg())
        self.mox.ReplayAll()
        register_instance('redis_cache', redis)

        # create new seeder subscription
        self.test_new_subscription_seeder()

        # delete subscription
        self.client.delete_subscription(
            self.project_id, self.object_id, self.seeder_subscription_id,
            seeder='salesforce')

        # subscription should be deleted
        self.assertRaises(
            NotFoundError, self.client.get_subscription,
            self.project_id, self.object_id, self.seeder_subscription_id)

    def test_get_object_subscriptions(self):
        """Make sure that we can get all subscriptions for a object."""
        pass

    def test_get_object_subscriptions_filter_delted(self):
        """Make sure that we can get all subscriptions for a object with delted
        subscriptions filtered out.
        """
        pass

    def test_get_subscription(self):
        """Make sure that we can retrieve an individual subscription."""
        pass

    #
    # Signals
    #

    def test_update_signal(self):
        """Make sure we can update object signals."""
        # create new object
        self.test_new_object()

        ret = self.client.update_object_signals(
            self.project_id, self.object_id,
            [{'key': 'baseobject',
              'value': ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw']}])
        signals = ret.get('signals')

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]['key'], 'baseobject')
        self.assertEqual(signals[0]['value'],
                         ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'])

    def test_update_signal_flat(self):
        """Make sure we can update object signals with the flat syntax."""
        # create new object
        self.test_new_object()

        signals = self.client.update_object_signals(
            self.project_id, self.object_id,
            {'baseobject': ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw']},
            flat=True)

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals['baseobject'],
                         ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'])

    def test_get_signals(self):
        """Make sure we can get object signals."""
        self.test_update_signal()

        ret = self.client.get_object_signals(self.project_id, self.object_id)
        signals = ret.get('signals')

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]['key'], 'baseobject')
        self.assertEqual(signals[0]['value'],
                         ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'])

    def test_get_signals_flat(self):
        """Make sure we can get object signals with the flat syntax."""
        self.test_update_signal()

        signals = self.client.get_object_signals(
            self.project_id, self.object_id, flat=True)

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals['baseobject'],
                         ['discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'])

    #
    # Preview
    #

    def test_get_preview(self):
        """Make sure that we can preview a provider configuration."""
        pass

    #
    # Collection
    #

    def test_get_collection(self):
        """Make sure that we can get the collection of a user."""
        pass

    def test_get_collection_object(self):
        """Make sure that we can get the collection object."""
        pass

    #
    # Fingerprint
    #

    def test_get_project_fingerprints(self):
        """Make sure that fingerprints can be retrieved."""
        pass

    def test_get_tenant_fingerprints(self):
        """Make sure that tenant fingerprints can be retrieved."""
        pass

    def test_get_fingerprint(self):
        """Make sure that an individual fingerprint can be retrieved."""
        pass

    def test_get_tenant_fingerprint_scores(self):
        """Make sure that fingerprint scores can be calculated ok."""
        pass

    def test_new_fingerprint(self):
        """Make sure that empty fingerprints can be created."""
        pass

    def test_get_fingerprint_debug(self):
        """Make sure that an individual debug fingerprint can be retrieved."""
        pass

    def test_update_fingerprint_from_content(self):
        """Make sure that fingerprints can be updated from content data."""
        pass

    def test_update_fingerprint_from_baseobject(self):
        """Make sure that fingerprints can be updated from baseobject data."""
        pass

    def test_update_fingerprint_from_items(self):
        """Make sure that fingerprints can be updated from items data."""
        pass

    def test_update_fingerprint_attributes(self):
        """Make sure that fingerprint attributes can be updated."""
        pass

    def test_delete_fingerprint(self):
        """Make sure that fingerprints can be deleted."""
        pass

    def test_delete_contributing_content_record(self):
        """Make sure that contributing content records can be deleted."""
        pass

    def test_update_contributing_content_record(self):
        """Make sure that contributing content records can be updated."""
        pass

    def test_delete_contributing_baseobject_record(self):
        """Make sure that contributing baseobject records can be deleted."""
        pass

    def test_delete_contributing_items_record(self):
        """Make sure that contributing items records can be deleted."""
        pass

    def test_copy_fingerprint(self):
        """Make sure that fingerprints can be copied."""
        pass

    def test_move_fingerprint(self):
        """Make sure that fingerprints can be moved."""
        pass


class TestTopicAPIMixinTasks(BaseTest, RequestsTestCaseMixin):
    """
    Tasks management.
    """

    def test_get_tasks(self):
        """Make sure that we can get tasks on a user."""
        self.requests.set_fixture(
            DummyResponse(200, json.dumps([{'id': 'task01'}, {'id': 'task02'}])),
            'GET', 'https://topic-api.squirro.com/v0/tenant01/tasks')

        client = SquirroClient('client01', 'secret01', tenant='tenant01',
                               requests=self.requests)
        client.access_token = 'token01'
        client.refresh_token = 'token02'

        tasks = client.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['id'], 'task01')

    def test_get_individual_task(self):
        """Make sure that we can get individual tasks."""
        self.requests.set_fixture(
            DummyResponse(200, json.dumps({'id': 'task01'})),
            'GET', 'https://topic-api.squirro.com/v0/tenant01/tasks/task01')

        client = SquirroClient('client01', 'secret01', tenant='tenant01',
                               requests=self.requests)
        client.access_token = 'token01'
        client.refresh_token = 'token02'

        task = client.get_task('task01')
        self.assertEqual(len(task), 1)
        self.assertEqual(task['id'], 'task01')

    def test_put_individual_task(self):
        """Make sure that we can update tasks."""
        self.requests.set_fixture(
            DummyResponse(200, json.dumps({'id': 'task01'})),
            'PUT', 'https://topic-api.squirro.com/v0/tenant01/tasks/task01')

        client = SquirroClient('client01', 'secret01', tenant='tenant01',
                               requests=self.requests)
        client.access_token = 'token01'
        client.refresh_token = 'token02'

        task = client.update_task('task01', schedule_when='*')
        self.assertEqual(len(task), 1)
        self.assertEqual(task['id'], 'task01')

        self.assertEqual(json.loads(self.requests.requests[0][2]['data']),
                         {'schedule_when': '*'})
