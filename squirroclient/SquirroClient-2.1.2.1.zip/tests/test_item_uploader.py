import json
import os.path
import shutil
import tempfile

from nose.tools import raises

from squirro.common.testing import MoxTestCaseMixin, TestCaseMixin, \
    DummyResponse
from squirro_client import ItemUploader, NotFoundError, SquirroClient
from requests import HTTPError


class TestItemUploaderBase(TestCaseMixin, MoxTestCaseMixin):

    def setUp(self):
        super(TestItemUploaderBase, self).setUp()

        self.kwargs = {}

    def _create_mox_client(self, **kwargs):
        """Creates a mock class to drop-into the `ItemUploader`"""
        self.mox_client = self.mox.CreateMock(SquirroClient)
        self.mox_client.tenant = 'tenant01'
        self.mox_client_class = self.mox.CreateMockAnything()
        self.mox_client_class.__call__(None, None,
                                       **kwargs)\
                             .AndReturn(self.mox_client)

        self.kwargs['client_cls'] = self.mox_client_class

    def _mock_constructor_project_id(self, processing_config=None,
                                     steps_config=None):
        """Mock everything needed for the constructor to run through"""
        self.mox_client.authenticate(refresh_token='token_passed')
        self.mox_client.get_project('project01').AndReturn({})
        self.mox_client.get_object('project01', 'default')\
                       .AndReturn({'id': 'default_id'})
        source_config = {'processing': {'filtering': {'enabled': False},
                                        'deduplication': {'policy': 'replace',
                                                          'enabled': True}},
                         'ext_id': 'Upload',
                         'tenant': 'tenant01',
                         'name': 'Upload'}

        if processing_config is not None:
            source_config['processing'].update(processing_config)

        if steps_config is not None:
            source_config['steps'] = steps_config

        self.mox_client.new_subscription('project01', 'default', 'bulk',
                                         source_config, private=True)\
                       .AndReturn({'source_id': 'source01',
                                   'source_secret': 'secret'})


class TestItemUploader(TestItemUploaderBase):
    """Make sure the `ItemUploader` works."""

    def setUp(self):
        super(TestItemUploader, self).setUp()

        # pass an invalid config-file name to avoid clashes with real files
        self.kwargs = {'config_file': 'foo.bar'}

        self._create_mox_client(cluster='https://next.squirro.net')

    @raises(NotFoundError)
    def test_only_title_nonexisting_project(self):
        """Should raise a `NotFoundError` since the project doesn't exist"""
        self.mox_client.authenticate(refresh_token='token_passed')
        self.mox_client.get_user_projects().AndReturn([])

        self.mox.ReplayAll()
        ItemUploader(token='token_passed', project_title='idontexist',
                     **self.kwargs)

    @raises(NotFoundError)
    def test_only_id_nonexisting_project(self):
        """Should raise a `NotFoundError` since the project doesn't exist"""
        self.mox_client.authenticate(refresh_token='token_passed')
        self.mox_client.get_project('idontexist').AndRaise(NotFoundError())
        self.mox.ReplayAll()

        ItemUploader(token='token_passed', project_id='idontexist',
                     **self.kwargs)

    @raises(NotFoundError)
    def test_only_id_existing_project_nonexisting_object(self):
        """Should raise a `NotFoundError` since the object doesn't exist"""
        self.mox_client.authenticate(refresh_token='token_passed')
        self.mox_client.get_project('project01').AndReturn({})
        self.mox_client.get_object('project01', 'idontexist')\
                       .AndRaise(NotFoundError)

        self.mox.ReplayAll()
        ItemUploader(token='token_passed', project_id='project01',
                     object_id='idontexist', **self.kwargs)

    @raises(NotFoundError)
    def test_only_title_existing_project_nonexisting_object(self):
        """Should raise a `NotFoundError` since the object doesn't exist"""
        self.mox_client.authenticate(refresh_token='token_passed')
        self.mox_client.get_user_projects()\
                       .AndReturn([{'id': 'project01', 'title': 'My Project'}])
        self.mox_client.get_object('project01', 'idontexist')\
                       .AndRaise(NotFoundError)
        self.mox.ReplayAll()

        ItemUploader(token='token_passed', project_title='My Project',
                     object_id='idontexist', **self.kwargs)

    def test_constructor_project_id(self):
        """Should retrieve `source_secret` and `source_id`"""
        self._mock_constructor_project_id()
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                **self.kwargs)
        self.assertEqual(uploader.source_id, 'source01')
        self.assertEqual(uploader.source_secret, 'secret')
        return uploader

    def test_upload_items(self):
        """Check that uploading items work"""
        self._mock_constructor_project_id()
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item01"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))

        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                **self.kwargs)
        uploader.upload([{'id': 'item01'}])

    def test_upload_items_batch_size_complete(self):
        """Check that uploading items works in complete batches"""
        self._mock_constructor_project_id()
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item01"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item02"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                batch_size=1,
                                **self.kwargs)
        uploader.upload([{'id': 'item01'}, {'id': 'item02'}])

    def test_upload_items_batch_size_incomplete(self):
        """Check that uploading items works with incomplete batches"""
        self._mock_constructor_project_id()
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item01"}, {"id": "item02"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item03"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                batch_size=2,
                                **self.kwargs)
        uploader.upload([{'id': 'item01'}, {'id': 'item02'}, {'id': 'item03'}])

    @raises(HTTPError)
    def test_upload_items_error(self):
        """Check that uploading items works with incomplete batches"""
        self._mock_constructor_project_id()
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data='[{"id": "item01"}, {"id": "item02"}]',
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(400, '{"error": "you did something wrong"}'))
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                **self.kwargs)
        uploader.upload([{'id': 'item01'}, {'id': 'item02'}])

    @raises(TypeError)
    def test_upload_invalid_keywords(self):
        """Check that invalid keyword types are being caught"""
        self._mock_constructor_project_id()
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                batch_size=2,
                                **self.kwargs)
        uploader.upload([{'id': 'item01', 'keywords': {'dict': dict()}}])

    def test_upload_keyword_transformation(self):
        """Check that keywords are being transformed into usable types"""
        self._mock_constructor_project_id()
        self.mox_client._perform_request('post',
                                         u'https://next.squirro.net/api/provider/v0/source/source01/secret',
                                         data=json.dumps([{'id': 'item01',
                                                           'keywords': {'set': ['a', 'b'],
                                                                        'string': ['hello!'],
                                                                        'list': ['a', 'c']}}]),
                                         headers={'Content-Type': 'application/json'})\
                       .AndReturn(DummyResponse(201, '{}'))
        self.mox.ReplayAll()

        uploader = ItemUploader(token='token_passed', project_id='project01',
                                batch_size=2,
                                **self.kwargs)
        uploader.upload([{'id': 'item01', 'keywords': {'set': set(['a', 'b']),
                                                       'string': 'hello!',
                                                       'list': ['a', 'c']}}])


class TestItemLoaderConfiguration(TestItemUploaderBase):
    """Factored out tests that need to set-up the `mox_client` themselves or
    don't need one"""

    @raises(ValueError)
    def test_no_token(self):
        """Check that the `ItemUploader` needs a token"""
        ItemUploader(**self.kwargs)

    @raises(ValueError)
    def test_no_project_id(self):
        """Check that the `ItemUploader` needs a `project_id` or a
        `project_title`"""
        ItemUploader(token='token_passed', **self.kwargs)

    def test_configuration_loading(self):
        """Check that specifying a file/section works"""
        self._create_mox_client(cluster='http://no.where.local')
        self._mock_constructor_project_id()
        self.mox.ReplayAll()

        tmpdir = tempfile.mkdtemp()
        tmpfile = os.path.join(tmpdir, 'squirro.ini')

        with open(tmpfile, 'w') as f:
            f.write('[some_section]\r\ncluster = http://no.where.local\r\n')

        ItemUploader(token='token_passed', project_id='project01',
                     batch_size=2, client_cls=self.mox_client_class,
                     config_file=tmpfile, config_section='some_section')

        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass  # we don't care about cleanup here

    def test_manual_urls(self):
        """Check that specifying manual urls for local dev-testing works"""
        self._create_mox_client(topic_api_url='http://topic',
                                user_api_url='http://user')
        self._mock_constructor_project_id()
        self.mox.ReplayAll()

        ItemUploader(token='token_passed', project_id='project01',
                     batch_size=2, client_cls=self.mox_client_class,
                     topic_api_url='http://topic', user_api_url='http://user',
                     provider_api_url='http://provider', cluster=None)

    def test_processing_config(self):
        """Ensure a processing configuration can be provided."""

        processing_config = {'my-step': {'enabled': True}}

        self._create_mox_client(cluster='http://example.com')
        self._mock_constructor_project_id(processing_config=processing_config)
        self.mox.ReplayAll()

        ItemUploader(token='token_passed', project_id='project01',
                     client_cls=self.mox_client_class,
                     cluster='http://example.com',
                     processing_config=processing_config)

    def test_steps_config(self):
        """Ensure a steps configuration can be provided."""

        steps_config = [{
            'before': 'deduplication', 'name': 'pipelet',
            'config': {
                'pipelet': 'squirro/Title Cleaner',
            },
        }]

        self._create_mox_client(cluster='http://example.com')
        self._mock_constructor_project_id(steps_config=steps_config)
        self.mox.ReplayAll()

        ItemUploader(token='token_passed', project_id='project01',
                     client_cls=self.mox_client_class,
                     cluster='http://example.com',
                     steps_config=steps_config)
