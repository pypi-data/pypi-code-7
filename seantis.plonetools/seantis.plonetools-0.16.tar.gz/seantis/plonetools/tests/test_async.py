from mock import Mock

from seantis.plonetools import async
from seantis.plonetools import tests


class TestAsync(tests.IntegrationTestCase):

    def setUp(self):
        super(TestAsync, self).setUp()
        self.old_logger = async.log
        async.log = Mock()

    def tearDown(self):
        super(TestAsync, self).tearDown()
        async.log = self.old_logger

    def test_register_clock_server(self):
        result = async.register('method', 60 * 60)
        self.assertEquals(result.method, 'method')
        self.assertTrue('method' in async._clockservers)

        async.clear_clockservers()
        self.assertTrue('method' not in async._clockservers)

    def test_clock_logger(self):
        logger = async.ClockLogger('method')

        logger.log('GET http://localhost:888/method HTTP/1.1 200')
        self.assertEquals(0, len(async.log.method_calls))

        logger.log('GET http://localhost:888/method HTTP/1.1 500')
        self.assertTrue('call.warn' in str(async.log.method_calls))
        self.assertTrue('500' in str(async.log.method_calls))

        logger.log('GET http://localhost:888/method HTTP/1.1')
        self.assertTrue('call.error' in str(async.log.method_calls))

        logger.log('')
        self.assertEquals(3, len(async.log.method_calls))

        logger.log('abcd')
        self.assertEquals(4, len(async.log.method_calls))
