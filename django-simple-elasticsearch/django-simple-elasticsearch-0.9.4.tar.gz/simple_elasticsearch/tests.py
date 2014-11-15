import contextlib

from django.db.models.signals import post_save, pre_delete
from django.test import TestCase
from elasticsearch import Elasticsearch
import mock

from . import settings as es_settings
from .mixins import ElasticsearchIndexMixin
from .models import Blog, BlogPost


@contextlib.contextmanager
def mock_signal_receiver(signal, wraps=None, **kwargs):
    """
    Borrowed from: https://github.com/dcramer/mock-django/blob/master/mock_django/signals.py

    Temporarily attaches a receiver to the provided ``signal`` within the scope
    of the context manager.
    The mocked receiver is returned as the ``as`` target of the ``with``
    statement.
    To have the mocked receiver wrap a callable, pass the callable as the
    ``wraps`` keyword argument. All other keyword arguments provided are passed
    through to the signal's ``connect`` method.
    >>> with mock_signal_receiver(post_save, sender=Model) as receiver:
    >>>     Model.objects.create()
    >>>     assert receiver.call_count = 1
    """
    if wraps is None:
        wraps = lambda *args, **kwargs: None

    receiver = mock.Mock(wraps=wraps)
    signal.connect(receiver, **kwargs)
    yield receiver
    signal.disconnect(receiver)


class ElasticsearchIndexMixinTestCase(TestCase):
    @mock.patch('elasticsearch.Transport.perform_request')
    def setUp(self, mock_perform_request):
        self.blog = Blog.objects.create(
            name='test blog name',
            description='test blog description'
        )

        # hack the return value to ensure we save some BlogPosts here;
        # without this mock, the post_save handler indexing blows up
        # as there is no real ES instance running
        mock_perform_request.return_value = (200, {})

        for x in xrange(1, 3):
            BlogPost.objects.create(
                blog=self.blog,
                title="blog post title {0}".format(x),
                slug="blog-post-title-{0}".format(x),
                body="blog post body {0}".format(x)
            )

    def test__get_es__with_default_settings(self):
        result = BlogPost.get_es()
        self.assertIsInstance(result, Elasticsearch)
        self.assertEqual(result.transport.hosts[0]['host'], '127.0.0.1')
        self.assertEqual(result.transport.hosts[0]['port'], 9200)

    def test__get_es__with_custom_server(self):
        # include a custom class here as the internal `_es` is cached, so can't reuse the
        # `ElasticsearchIndexClassDefaults` global class (see above).
        class ElasticsearchIndexClassCustomSettings(ElasticsearchIndexMixin):
            pass

        with self.settings(ELASTICSEARCH_SERVER=['search.example.com:9201']):
            reload(es_settings)
            result = ElasticsearchIndexClassCustomSettings.get_es()
            self.assertIsInstance(result, Elasticsearch)
            self.assertEqual(result.transport.hosts[0]['host'], 'search.example.com')
            self.assertEqual(result.transport.hosts[0]['port'], 9201)

        reload(es_settings)

    def test__get_es__with_custom_connection_settings(self):
        # include a custom class here as the internal `_es` is cached, so can't reuse the
        # `ElasticsearchIndexClassDefaults` global class (see above).
        class ElasticsearchIndexClassCustomSettings(ElasticsearchIndexMixin):
            pass

        with self.settings(ELASTICSEARCH_CONNECTION_PARAMS={'hosts': ['search2.example.com:9202'], 'sniffer_timeout': 15}):
            reload(es_settings)
            result = ElasticsearchIndexClassCustomSettings.get_es()
            self.assertIsInstance(result, Elasticsearch)
            self.assertEqual(result.transport.hosts[0]['host'], 'search2.example.com')
            self.assertEqual(result.transport.hosts[0]['port'], 9202)
            self.assertEqual(result.transport.sniffer_timeout, 15)
        reload(es_settings)

    # @mock.patch('elasticsearch.Transport.perform_request')
    # @mock.patch('simple_elasticsearch.mixins.ElasticsearchIndexMixin.index_add')
    # @mock.patch('simple_elasticsearch.models.BlogPost.save_handler')
    # def test__save_handler(self, mock_save_handler, mock_index):
    def test__save_handler(self):
        next_post_id = BlogPost.objects.latest('pk').pk + 1

        # mock_perform_request.return_value = (200, {
        #     "_index": "blog",
        #     "_type": "posts",
        #     "_id": str(next_post_id),
        #     "_version": 1,
        #     "created": True
        # })
        with mock_signal_receiver(post_save, sender=BlogPost) as receiver:
            post = BlogPost.objects.create(
                blog=self.blog,
                title="blog post title {0}".format(next_post_id),
                slug="blog-post-title-{0}".format(next_post_id),
                body="blog post body {0}".format(next_post_id)
            )
            assert receiver.call_count == 1
            assert receiver.call_args[1]['sender'] == BlogPost
            assert receiver.call_args[1]['instance'] == post

    def test__delete_handler(self):
        with mock_signal_receiver(pre_delete, sender=BlogPost) as receiver:
            post = BlogPost.objects.latest('pk')
            post.delete()
            assert receiver.call_count == 1
            assert receiver.call_args[1]['sender'] == BlogPost
            assert receiver.call_args[1]['instance'] == post




class ElasticsearchSearchFormTestCase(TestCase):
    pass


class ElasticsearchGetDocumentTestCase(TestCase):
    pass