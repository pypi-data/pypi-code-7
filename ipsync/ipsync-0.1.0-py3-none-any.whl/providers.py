# pylint: disable=R0903
"""Defines cloud providers and exposes ProviderFactory."""

import abc
import logging
import re
import requests
import requests.exceptions
from bs4 import BeautifulSoup


class AbstractProvider(object):

    """Used to define the provider interface, all providers must inherit from GenericProvider."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_ip(self, ip, dry_run):
        """Update the provider's DNS records with the new IP address.

        This must be overridden by the provider class

        :param: ip: New IP address to update at the provider
        :return: None
        """


class GenericProvider(AbstractProvider):

    """Set the config data when a provider is instantiated.

    All providers must inherit from this class.
    """

    def __init__(self, name, config):
        """Create a new provider.

        :param name:
        :param config: Provider specific config
        :return:
        """
        self._name = name
        self._config = config

    @abc.abstractmethod
    def update_ip(self, ip, dry_run):
        """Update the provider's DNS records with the new IP address.

        This must be overridden by the provider class

        :param: ip: New IP address to update at the provider
        :return: None
        """


class InvalidProvider(GenericProvider):

    """Used when no provider could be found matching the config yaml."""

    def update_ip(self, ip, dry_run):
        """Log to file and do nothing."""
        logger = logging.getLogger()

        logger.error('Unable to find provider %s', self._name)
        return False


class Rackspace(GenericProvider):

    """Rackspace cloud provider. Allows updating IP address of Rackspace Cloud DNS."""

    def update_ip(self, ip, dry_run):
        """Update the IP address stored within a Rackspace Cloud DNS domain.

        This function will create the hostname if it does not already exist.

        :param ip:
        :return:
        """
        logger = logging.getLogger()

        logger.debug('RAX config: %s', self._config)
        logger.info('Updating RAX with IP %s', ip)

        return False


class Namecheap(GenericProvider):

    """Namecheap provider. Allows updating an IP address of a pre-configured domain.

    DDNS must be configured in namecheap's control panel before this will work.
    """

    # Success:
    # <?xml version="1.0" encoding="UTF-8"?>
    # <interface-response>
    #     <Command>SETDNSHOST</Command>
    #     <Language>eng</Language>
    #     <IP>1.36.217.16</IP>
    #     <ErrCount>0</ErrCount>
    #     <ResponseCount>0</ResponseCount>
    #     <Done>true</Done>
    #     <debug />
    # </interface-response>

    # Error:
    # <?xml version="1.0" encoding="UTF-8"?>
    # <interface-response>
    #     <Command>SETDNSHOST</Command>
    #     <Language>eng</Language>
    #     <ErrCount>1</ErrCount>
    #     <errors>
    #         <Err1>Domain name not active</Err1>
    #     </errors>
    #     <ResponseCount>1</ResponseCount>
    #     <responses>
    #         <response>
    #             <ResponseNumber>316154</ResponseNumber>
    #             <ResponseString>Validation error; not active; domain name(s)</ResponseString>
    #         </response>
    #     </responses>
    #     <Done>true</Done>
    #     <debug />
    # </interface-response>

    def update_ip(self, ip, dry_run):
        """Update the IP address for a domain hosted at namecheap."""
        logger = logging.getLogger()

        endpoint = 'https://dynamicdns.park-your-domain.com/' \
                   'update?host={host}&domain={domain}&password={password}&ip={ip}'

        for domain in self._config:
            host = self._config[domain].get('hostname')
            password = self._config[domain].get('password')

            if dry_run:
                logger.info('dry_run: True. Will not update %s.%s', host, domain)
                continue

            try:
                response = requests.get(endpoint.format(host=host,
                                                        domain=domain,
                                                        password=password,
                                                        ip=ip))
            except requests.exceptions.RequestException as error:
                logger.error(error)
                continue

            soup = BeautifulSoup(response.text)
            for error in soup.find_all(re.compile(r'(err\d)')):
                logger.error('Received error when updating %s.%s: %s',
                             host, domain, error.text)
                break
            else:
                logger.info('Successfully updated %s.%s with new IP %s', host, domain, ip)


def get_provider(name, config):
    """Return a provider class which will update the IP address at that specific provider.

    :param name: Name of the provider from the yaml config.
    :param config: Parsed data from the yaml config.
    :return: Provider class.
    """
    for subclass in GenericProvider.__subclasses__():  # pylint: disable=E1101
        if subclass.__name__.lower() == name.lower():
            provider = subclass(name, config)
            break
    else:
        provider = InvalidProvider(name, config)

    return provider
