#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.beaker.metadirectives import IBeakerSessionConfiguration

# import Zope3 packages
from zope.component.security import PublicPermission
from zope.component.zcml import utility

# import local packages
from ztfy.beaker.session import BeakerMemorySessionConfiguration, BeakerDBMSessionConfiguration, \
    BeakerFileSessionConfiguration, BeakerMemcachedSessionConfiguration, BeakerAlchemySessionConfiguration


def memorySession(context, name='', **kwargs):
    """Beaker memory session configuration declaration"""
    config = BeakerMemorySessionConfiguration()
    for key, value in kwargs.iteritems():
        setattr(config, key, value)
    utility(context, IBeakerSessionConfiguration, config, permission=PublicPermission, name=name)


def dbmSession(context, name='', **kwargs):
    """Beaker DBM session configuration declaration"""
    config = BeakerDBMSessionConfiguration()
    for key, value in kwargs.iteritems():
        setattr(config, key, value)
    utility(context, IBeakerSessionConfiguration, config, permission=PublicPermission, name=name)


def fileSession(context, name='', **kwargs):
    """Beaker file session configuration declaration"""
    config = BeakerFileSessionConfiguration()
    for key, value in kwargs.iteritems():
        setattr(config, key, value)
    utility(context, IBeakerSessionConfiguration, config, permission=PublicPermission, name=name)


def memcachedSession(context, name='', **kwargs):
    """Beaker memcached session configuration declaration"""
    config = BeakerMemcachedSessionConfiguration()
    for key, value in kwargs.iteritems():
        setattr(config, key, value)
    utility(context, IBeakerSessionConfiguration, config, permission=PublicPermission, name=name)


def alchemySession(context, name='', **kwargs):
    """Beaker SQLAlchemy session configuration declaration"""
    config = BeakerAlchemySessionConfiguration()
    for key, value in kwargs.iteritems():
        setattr(config, key, value)
    utility(context, IBeakerSessionConfiguration, config, permission=PublicPermission, name=name)
