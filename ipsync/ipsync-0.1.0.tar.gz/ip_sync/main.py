"""ipsync.

Usage:
    ipsync [options] <command>

Options:
    -h --help               Show this screen.
    -v --version            Show version.
    -c FILE --config=FILE   Configuration FILE to use [default: ~/.config/ipsync.conf]
    --dry-run               Run but don't make any changes.

Available commands:
    update                  Resolve current IP address and update all providers

"""

import sys
import logging
import requests
import requests.exceptions
import ipaddress
from docopt import docopt
from schema import Schema, Use, SchemaError
import yaml

from ip_sync.version import __version__
from ip_sync.providers import get_provider


def resolve_ip():
    """Resolve the external IP address of this machine.

    :return: External IP address
    """
    logger = logging.getLogger()
    logger.info('Resolving IP...')

    try:
        response = requests.get('https://icanhazip.com/')
    except requests.exceptions.RequestException as error:
        logger.error('Exception raised during request: %s', error)
        return None

    if response.status_code == requests.codes['ok']:
        try:
            ip = ipaddress.ip_address(response.text.strip())
        except ValueError as error:
            logger.error('Could not receive a valid IP address: %s', error.args)
            return None

        logger.info('Received IP address %s', ip)
        return ip
    else:
        logger.error('Unable to retrieve IP address, %s status code received',
                     response.status_code)
        return None


def load_config(config_file):
    """Load the configuration yaml from disk."""
    logger = logging.getLogger()

    logger.info('Loading configuration file from %s', config_file.name)

    data = yaml.safe_load(config_file)
    logger.debug(data)

    return data


def command_update(arguments):
    """Update all providers with a new IP."""
    logger = logging.getLogger()

    logger.info('Running update')

    logger = logging.getLogger()
    config = load_config(arguments['--config'])
    ip = resolve_ip()

    if not ip:
        logger.error('No IP address retrieved, exiting.')
        return sys.exit(1)

    for provider in config:
        logger.debug('Parsing provider: %s', provider)
        provider_class = get_provider(provider.lower(), config[provider])
        provider_class.update_ip(ip, dry_run=arguments['--dry-run'])


def main():
    """The main entrypoint to ip_sync."""
    log_format = "%(asctime)s %(levelname)-7s " \
                 "[%(filename)20s:%(lineno)-4s %(funcName)-20s] " \
                 "%(message)s"
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format)

    commands = {'update': command_update}

    arguments = docopt(__doc__, version='ipsync %s' % __version__)
    schema = Schema({
        '--config': Use(open, error='config file must be readable'),
        object: object
    })
    try:
        arguments = schema.validate(arguments)
    except SchemaError as error:
        return sys.exit(error)

    if arguments['<command>'] in commands:
        command = commands[arguments['<command>']]
        command(arguments)


if __name__ == '__main__':
    main()
