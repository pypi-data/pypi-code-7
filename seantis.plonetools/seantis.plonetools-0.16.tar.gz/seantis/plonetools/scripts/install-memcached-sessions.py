""" Installs the BeakerSessionDataManager into the Zope Root to enable
memcached sessions with collective.beaker and
Products.BeakerSessionDataManager.

Run as follows:

bin/instance run <path to seantis.plonetools>
/seantis/plonetools/scripts/install-memcached-sessions.py

"""


import transaction
import logging
log = logging.getLogger('seantis.plonetools')


def main(app):
    try:
        from Products.BeakerSessionDataManager.sessiondata import (
            addBeakerSessionDataManager, BeakerSessionDataManager
        )
    except ImportError:
        log.error('BeakerSessionDataManager not found.')
        return

    if 'session_data_manager' in app:
        if isinstance(app['session_data_manager'], BeakerSessionDataManager):
            log.warn('BeakerSessionDataManager is already installed.')
            return

        del app['session_data_manager']

    dispatcher = app.manage_addProduct['BeakerSessionDataManager']
    addBeakerSessionDataManager(
        dispatcher, 'session_data_manager', 'Beaker Session Data Manager'
    )
    transaction.commit()

    log.info('Sucessfully installed BeakerSessionDataManager')

if 'app' in locals():
    main(locals()['app'])
