#
# Copyright (c) 2014 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import Bool, TextLine, Int, Choice, InterfaceField

# import local packages

from ztfy.beaker import _


class IBeakerSessionConfiguration(Interface):
    """Beaker session base configuration"""

    type = TextLine(title=_("Storage type"),
                    required=False,
                    readonly=True)

    auto = Bool(title=_("Auto save session data?"),
                required=True,
                default=True)

    environ_key = TextLine(title=_("Request environment key"),
                           description=_("Name of the WSGI environment key holding session data"),
                           default=u'beaker.session')

    invalidate_corrupt = Bool(title=_("Invalide corrupt"),
                              description=_("How to handle corrupt data when loading. When set to True, then corrupt "
                                            "data will be silently invalidated and a new session created, otherwise "
                                            "invalid data will cause an exception."),
                              required=False,
                              default=False)

    key = TextLine(title=_("Cookie name"),
                   description=_("The name the cookie should be set to"),
                   required=False,
                   default=u'beaker.session.id')

    timeout = Int(title=_("Session timeout"),
                  description=_("How long session data is considered valid. This is used regardless of the cookie "
                                "being present or not to determine whether session data is still valid"),
                  required=False,
                  default=3600)

    cookie_expires = Bool(title=_("Expiring cookie?"),
                          description=_("Does cookie have an expiration date?"),
                          required=False,
                          default=False)

    cookie_domain = TextLine(title=_("Cookie domain"),
                             description=_("Domain to use for the cookie"),
                             required=False)

    cookie_path = TextLine(title=_("Cookie path"),
                           description=_("Path to use for the cookie"),
                           required=False,
                           default=u'/')

    secure = Bool(title=_("Secure cookie?"),
                  description=_("Whether or not the cookie should only be sent over SSL"),
                  required=False,
                  default=False)

    httponly = Bool(title=_("HTTP only?"),
                    description=_("Whether or not the cookie should only be accessible by the browser not by "
                                  "JavaScript"),
                    required=False,
                    default=False)

    encrypt_key = TextLine(title=_("Encryption key"),
                           description=_("The key to use for the local session encryption, if not provided the "
                                         "session will not be encrypted"),
                           required=False)

    validate_key = TextLine(title=_("Validation key"),
                            description=_("The key used to sign the local encrypted session"),
                            required=False)

    lock_dir = TextLine(title=_("Lock directory"),
                        description=_("Used to coordinate locking and to ensure that multiple processes/threads "
                                      "aren't attempting to re-create the same value at the same time"),
                        required=True)


class IBeakerSessionConfigurationInfo(Interface):
    """Beaker session configuration info"""

    configuration = InterfaceField(title=_("Configuration interface"),
                                   required=False)

    def getConfigurationDict(self):
        """Get configuration options as dict"""


class IBeakerMemorySessionConfiguration(IBeakerSessionConfiguration):
    """Beaker memory session configuration"""


class IBeakerBaseFileSessionConfiguration(IBeakerSessionConfiguration):
    """Beaker file storage session configuration"""

    data_dir = TextLine(title=_("Data directory"),
                        description=_("Absolute path to the directory that stores the files"),
                        required=True)


class IBeakerDBMSessionConfiguration(IBeakerBaseFileSessionConfiguration):
    """Beaker DBM file storage session configuration"""


class IBeakerFileSessionConfiguration(IBeakerBaseFileSessionConfiguration):
    """Beaker file session configuration"""


class IBeakerDatabaseSessionConfiguration(IBeakerSessionConfiguration):
    """Beaker database storage session configuration"""

    url = TextLine(title=_("Database URL"),
                   required=True)


class IBeakerMemcachedSessionConfiguration(IBeakerDatabaseSessionConfiguration):
    """Beaker memached storage session configuration"""

    url = TextLine(title=_("Memcached servers URL"),
                   description=_("Semi-colon separated list of memcached servers"),
                   required=True)

    memcached_module = Choice(title=_("Memcached module to use"),
                              description=_("Specifies which memcached client library should be imported"),
                              required=True,
                              values=(u'auto', u'memcache', u'cmemcache', u'pylibmc'),
                              default=u'auto')


class IBeakerAlchemySessionConfiguration(IBeakerDatabaseSessionConfiguration):
    """Beaker SQLAlchemy storage session configuration"""

    url = TextLine(title=_("SQLAlchemy database URL"),
                   description=_("Valid SQLAlchemy database connection string"),
                   required=True)

    schema_name = TextLine(title=_("Database schema name"),
                           description=_("The schema name to use in the database"),
                           required=False)

    table_name = TextLine(title=_("Database table name"),
                          description=_("The table name to use in the database"),
                          required=True,
                          default=u'beaker_session')
