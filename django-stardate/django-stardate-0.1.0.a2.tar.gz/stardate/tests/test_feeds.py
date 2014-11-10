from django.test import TestCase
from django.test.client import Client

# from stardate.feeds import LatestPostsFeed
from stardate.tests.factories import create_blog, create_post
from stardate.utils import get_post_model


Post = get_post_model()


class LatestFeedTestCase(TestCase):
    def setUp(self):
        b = create_blog()
        create_post(
            blog=b,
            body='# Headline\n\nAnd some text.\n'
        )
        self.client = Client()

    def test_feed(self):
        response = self.client.get('/test-blog/rss/')

        self.assertEqual(response.status_code, 200)
