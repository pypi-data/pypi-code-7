# pylint: disable=C0111,R0903
from mock import patch
from ipaddress import IPv4Address, IPv6Address
import six
import requests.exceptions
import schema

from ip_sync.test import TestBase
from ip_sync import main


class TestMain(TestBase):
    @patch('requests.get')
    def test_resolve_ipv4(self, request_mock):
        ip = '127.0.0.1'

        request_mock.return_value.status_code = 200
        request_mock.return_value.text = six.u('%s\n' % ip)

        self.assertEquals(main.resolve_ip(), IPv4Address(six.u(ip)))

    @patch('requests.get')
    def test_resolve_ipv6(self, request_mock):
        for ip in ['2001:0db8:85a3:0000:0000:8a2e:0370:7334',
                   '2001:0db8:85a3::8a2e:0370:7334',
                   '::1']:
            request_mock.return_value.status_code = 200
            request_mock.return_value.text = six.u('%s\n' % ip)

            self.assertEquals(main.resolve_ip(), IPv6Address(six.u(ip)))

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_error_status_code(self, request_mock):
        request_mock.return_value.status_code = 500
        request_mock.return_value.text = six.u('An error occurred')

        self.assertIsNone(main.resolve_ip())

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_exception(self, request_mock):
        request_mock.side_effect = requests.exceptions.ConnectionError

        self.assertIsNone(main.resolve_ip())

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_invalid_data(self, request_mock):
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = six.u('some random data\n')

        self.assertIsNone(main.resolve_ip())

    def test_load_config(self):
        config_data = main.load_config(self._config_file)
        self.assertIsNotNone(config_data.get('rackspace'))
        self.assertIsNotNone(config_data.get('namecheap'))
        self.assertIsNotNone(config_data['rackspace'].get('api_username'))
        self.assertIsNotNone(config_data['namecheap'].get('test.com'))
        self.assertIsNotNone(config_data['namecheap']['test.com'].get('hostname'))

    @patch('ip_sync.main.get_provider')
    @patch('ip_sync.main.resolve_ip')
    def test_command_update(self, resolve_ip_mock, get_provider_mock):
        resolve_ip_mock.return_value = IPv4Address(six.u('127.0.0.1'))
        main.command_update(self._args)

        resolve_ip_mock.assert_called_once_with()
        get_provider_mock.assert_any_call('rackspace', self._config_data['rackspace'])
        get_provider_mock.assert_any_call('namecheap', self._config_data['namecheap'])

    @patch('ip_sync.main.get_provider')
    @patch('sys.exit')
    @patch('ip_sync.main.resolve_ip')
    def test_command_update_exits_when_no_ip(self, resolve_ip_mock, exit_mock, get_provider_mock):
        resolve_ip_mock.return_value = None
        main.command_update(self._args)

        resolve_ip_mock.assert_called_once_with()
        self.assertEqual(exit_mock.call_count, 1)
        self.assertEqual(get_provider_mock.call_count, 0)

    @patch.object(schema.Schema, 'validate')
    @patch('ip_sync.main.docopt')
    @patch('ip_sync.main.command_update')
    def test_main(self, command_update_mock, docopt_mock, schema_mock):
        docopt_mock.return_value = self._args
        schema_mock.return_value = self._args

        main.main()

        command_update_mock.assert_called_once_with(self._args)
        self.assertEqual(docopt_mock.call_count, 1)
        self.assertEqual(schema_mock.call_count, 1)

    @patch('sys.exit')
    @patch.object(schema.Schema, 'validate')
    @patch('ip_sync.main.docopt')
    @patch('ip_sync.main.command_update')
    def test_main_exits_on_schema_error(self, command_update_mock, docopt_mock, schema_mock,
                                        exit_mock):
        docopt_mock.return_value = self._args
        schema_mock.side_effect = schema.SchemaError(None, None)

        main.main()

        self.assertEqual(command_update_mock.call_count, 0)
        self.assertEqual(docopt_mock.call_count, 1)
        self.assertEqual(schema_mock.call_count, 1)
        self.assertEqual(exit_mock.call_count, 1)
