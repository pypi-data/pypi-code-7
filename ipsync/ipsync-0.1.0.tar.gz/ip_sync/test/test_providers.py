# pylint: disable=C0111,R0903
from ipaddress import IPv4Address
import six
from mock import patch, Mock
from logging import RootLogger
import requests.exceptions

from ip_sync.test import TestBase
from ip_sync import providers


class TestProviders(TestBase):
    def setUp(self):
        super(TestProviders, self).setUp()

    def test_get_invalid_provider(self):
        self.assertIsInstance(providers.get_provider('invalid-provider-123456', None),
                              providers.InvalidProvider)

    def test_get_providers(self):
        provider_data = {
            'invalid-provider-123456': (None, providers.InvalidProvider),
            'rackspace': (self._config_data.get('rackspace'), providers.Rackspace),
            'namecheap': (self._config_data.get('namecheap'), providers.Namecheap),
        }

        for name in self._config_data:
            self.assertIsNotNone(provider_data.get(name), 'No Provider exists for \'%s\'' % name)
            config, class_type = provider_data.get(name)
            result = providers.get_provider(name, config)

            self.assertIsInstance(result, class_type,
                                  'result \'%s\' is not an instance of \'%s\''
                                  % (result.__class__.__name__, class_type))

            self.assertEqual(result._name, name)  # pylint: disable=W0212
            self.assertEqual(result._config, config)  # pylint: disable=W0212

    def test_invalid_provider_update(self):
        provider = providers.get_provider('invalid-provider-1234', None)
        self.assertIsInstance(provider, providers.InvalidProvider)
        provider.update_ip(IPv4Address(six.u('127.0.0.1')), False)

    @patch('requests.get')
    def test_rackspace_update(self, requests_get_mock):
        requests_get_mock.return_value.status_code = 200
        requests_get_mock.return_value.text = ''

        provider = providers.get_provider('rackspace', self._config_data['rackspace'])
        self.assertIsInstance(provider, providers.Rackspace)
        provider.update_ip(IPv4Address(six.u('127.0.0.1')), False)

    @patch('requests.get')
    def test_namecheap_dry_run(self, requests_get_mock):
        provider = providers.get_provider('namecheap', self._config_data['namecheap'])
        self.assertIsInstance(provider, providers.Namecheap)
        provider.update_ip(IPv4Address(six.u('127.0.0.1')), True)

        self.assertEqual(0, requests_get_mock.call_count)

    @patch('logging.getLogger')
    @patch('requests.get')
    def test_namecheap_logs_error_on_requests_exception(self, requests_get_mock, logging_mock):
        requests_get_mock.side_effect = requests.exceptions.ConnectTimeout('ConnectTimeout')

        provider = providers.get_provider('namecheap', self._config_data['namecheap'])
        self.assertIsInstance(provider, providers.Namecheap)

        provider.update_ip(IPv4Address(six.u('127.0.0.1')), False)

        self.assertEqual(0, logging_mock().info.call_count)
        self.assertEqual(2, logging_mock().error.call_count)

    @patch('logging.getLogger')
    @patch('requests.get')
    def test_namecheap_logs_error_when_error_from_api(self, requests_get_mock, logging_mock):
        requests_get_mock.return_value.status_code = 200
        requests_get_mock.return_value.text = """<?xml version="1.0" encoding="UTF-8"?>
<interface-response>
    <Command>SETDNSHOST</Command>
    <Language>eng</Language>
    <ErrCount>1</ErrCount>
    <errors>
        <Err1>Domain name not active</Err1>
    </errors>
    <ResponseCount>1</ResponseCount>
    <responses>
        <response>
            <ResponseNumber>316154</ResponseNumber>
            <ResponseString>Validation error; not active; domain name(s)</ResponseString>
        </response>
    </responses>
    <Done>true</Done>
    <debug />
</interface-response>"""
        logging_mock.return_value = Mock(spec=RootLogger)

        provider = providers.get_provider('namecheap', self._config_data['namecheap'])
        self.assertIsInstance(provider, providers.Namecheap)

        provider.update_ip(IPv4Address(six.u('127.0.0.1')), False)

        self.assertEqual(0, logging_mock().info.call_count)
        self.assertEqual(2, logging_mock().error.call_count)

    @patch('logging.getLogger')
    @patch('requests.get')
    def test_namecheap_logs_success_when_success_from_api(self, requests_get_mock, logging_mock):
        requests_get_mock.return_value.status_code = 200
        requests_get_mock.return_value.text = """<?xml version="1.0" encoding="UTF-8"?>
<interface-response>
    <Command>SETDNSHOST</Command>
    <Language>eng</Language>
    <IP>1.36.217.16</IP>
    <ErrCount>0</ErrCount>
    <ResponseCount>0</ResponseCount>
    <Done>true</Done>
    <debug />
</interface-response>"""
        logging_mock.return_value = Mock(spec=RootLogger)

        provider = providers.get_provider('namecheap', self._config_data['namecheap'])
        self.assertIsInstance(provider, providers.Namecheap)

        provider.update_ip(IPv4Address(six.u('127.0.0.1')), False)

        self.assertEqual(2, logging_mock().info.call_count)
        self.assertEqual(0, logging_mock().error.call_count)
