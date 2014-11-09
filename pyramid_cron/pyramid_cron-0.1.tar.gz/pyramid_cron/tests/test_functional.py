from datetime import datetime
from unittest import TestCase

from pyramid import testing

from .. import CronView, includeme


class TestFunctional(TestCase):
    def test_simple_task(self):
        called = []

        def mytask(system):
            called.append(True)

        with testing.testConfig() as config:
            config.include(includeme)
            config.add_cron_task(mytask)
            request = testing.DummyRequest(remote_addr='127.0.0.1')
            CronView(request)()
            self.assertEqual(called, [True])

    def test_forbidden_ip(self):
        called = []

        def mytask(system):
            called.append(True)

        with testing.testConfig() as config:
            config.include(includeme)
            config.add_cron_task(mytask)
            request = testing.DummyRequest(remote_addr='1.2.3.4')
            response = CronView(request)()
            self.assertIn('fail', response)
            self.assertEqual(called, [])

    def test_scheduled_task(self):
        called = []

        def mytask_even_minutes(system):
            called.append('even')

        def mytask_odd_minutes(system):
            called.append('odd')

        with testing.testConfig() as config:
            config.include(includeme)
            config.add_cron_task(mytask_even_minutes, min=range(0, 60, 2))
            config.add_cron_task(mytask_odd_minutes, min=range(1, 60, 2))
            request = testing.DummyRequest(remote_addr='127.0.0.1')
            now = datetime.now()
            CronView(request)()
            if (now.minute % 2) == 1:
                should_be = 'odd'
            else:
                should_be = 'even'
            self.assertEqual(called, [should_be])
