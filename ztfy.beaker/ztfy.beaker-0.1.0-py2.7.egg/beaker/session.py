#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
from persistent import Persistent

# import Zope3 interfaces
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.configuration.exceptions import ConfigurationError
from zope.schema.interfaces import IVocabularyFactory
from zope.session.interfaces import ISessionDataContainer, ISessionData, ISessionPkgData

# import local interfaces
from ztfy.beaker.interfaces import IBeakerSessionUtility
from ztfy.beaker.metadirectives import IBeakerFileSessionConfiguration, IBeakerSessionConfiguration, \
    IBeakerMemcachedSessionConfiguration, IBeakerSessionConfigurationInfo, \
    IBeakerMemorySessionConfiguration, IBeakerDBMSessionConfiguration, IBeakerAlchemySessionConfiguration

# import Zope3 packages
from zope.component import queryUtility
from zope.container.contained import Contained
from zope.interface import implements, classProvides
from zope.minmax import Maximum
from zope.schema import getFieldNames
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.utils.request import getRequest

from ztfy.beaker import _


class BeakerPkgData(dict):
    """Beaker package data

    See zope.session.interfaces.ISessionPkgData

        >>> session = BeakerPkgData()
        >>> ISessionPkgData.providedBy(session)
        True
    """

    implements(ISessionPkgData)


class BeakerSessionData(dict):
    """Beaker session data"""

    implements(ISessionData)

    _lastAccessTime = None

    def __init__(self):
        self._lastAccessTime = Maximum(0)

    def __getitem__(self, key):
        try:
            return super(BeakerSessionData, self).__getitem__(key)
        except KeyError:
            data = self[key] = BeakerPkgData()
            return data

    # we include this for parallelism with setLastAccessTime
    @property
    def lastAccessTime(self):
        # this conditional is for legacy sessions; this comment and
        # the next two lines will be removed in a later release
        if self._lastAccessTime is None:
            return self.__dict__.get('lastAccessTime', 0)
        return self._lastAccessTime.value

    # we need to set this value with setters in order to get optimal conflict
    # resolution behavior
    @lastAccessTime.setter
    def lastAccessTime(self, value):
        # this conditional is for legacy sessions; this comment and
        # the next two lines will be removed in a later release
        if self._lastAccessTime is None:
            self._lastAccessTime = Maximum(0)
        self._lastAccessTime.value = value


class BeakerSessionUtility(Persistent, Contained):
    """Beaker base session utility"""

    implements(ISessionDataContainer, IBeakerSessionUtility)

    timeout = FieldProperty(ISessionDataContainer['timeout'])
    resolution = FieldProperty(ISessionDataContainer['resolution'])

    configuration_name = FieldProperty(IBeakerSessionUtility['configuration_name'])

    def get(self, key, default=None):
        return self[key]

    def _getSession(self):
        request = getRequest()
        config = queryUtility(IBeakerSessionConfiguration, name=self.configuration_name or u'')
        if config is None:
            raise ConfigurationError(_("Can't find beaker configuration"))
        session = request.get(config.environ_key)
        if session is None:
            raise ConfigurationError(_("No Beaker session defined in current request"))
        return session

    def __getitem__(self, pkg_id):
        session = self._getSession()
        result = session.get(pkg_id)
        if result is None:
            result = session[pkg_id] = BeakerSessionData()
        return result

    def __setitem__(self, pkg_id, session_data):
        session = self._getSession()
        session[pkg_id] = session_data


class BeakerSessionConfiguration(Persistent, Contained):
    """Beaker base session configuration"""

    implements(IBeakerSessionConfiguration, IBeakerSessionConfigurationInfo)

    auto = FieldProperty(IBeakerSessionConfiguration['auto'])
    environ_key = FieldProperty(IBeakerSessionConfiguration['environ_key'])
    invalidate_corrupt = FieldProperty(IBeakerSessionConfiguration['invalidate_corrupt'])
    key = FieldProperty(IBeakerSessionConfiguration['key'])
    cookie_expires = FieldProperty(IBeakerSessionConfiguration['cookie_expires'])
    cookie_domain = FieldProperty(IBeakerSessionConfiguration['cookie_domain'])
    cookie_path = FieldProperty(IBeakerSessionConfiguration['cookie_path'])
    secure = FieldProperty(IBeakerSessionConfiguration['secure'])
    httponly = FieldProperty(IBeakerSessionConfiguration['httponly'])
    encrypt_key = FieldProperty(IBeakerSessionConfiguration['encrypt_key'])
    validate_key = FieldProperty(IBeakerSessionConfiguration['validate_key'])
    lock_dir = FieldProperty(IBeakerSessionConfiguration['lock_dir'])

    configuration = None

    def getConfigurationDict(self):
        result = {'session.auto': True}
        if self.configuration:
            for fieldname in getFieldNames(self.configuration):
                value = getattr(self, fieldname, None)
                if value is not None:
                    result['session.' + fieldname] = value
        return result


class BeakerMemorySessionConfiguration(BeakerSessionConfiguration):
    """Beaker memory session configuration"""

    implements(IBeakerMemorySessionConfiguration)

    configuration = IBeakerMemorySessionConfiguration

    type = 'memory'


class BeakerDBMSessionConfiguration(BeakerSessionConfiguration):
    """Beaker DBM session configuration"""

    implements(IBeakerDBMSessionConfiguration)

    configuration = IBeakerDBMSessionConfiguration

    type = 'dbm'
    data_dir = FieldProperty(IBeakerFileSessionConfiguration['data_dir'])


class BeakerFileSessionConfiguration(BeakerSessionConfiguration):
    """Beaker file session configuration"""

    implements(IBeakerFileSessionConfiguration)

    configuration = IBeakerFileSessionConfiguration

    type = 'file'
    data_dir = FieldProperty(IBeakerFileSessionConfiguration['data_dir'])


class BeakerMemcachedSessionConfiguration(BeakerSessionConfiguration):
    """Beaker memcached session configuration"""

    implements(IBeakerMemcachedSessionConfiguration)

    configuration = IBeakerMemcachedSessionConfiguration

    type = 'ext:memcached'
    url = FieldProperty(IBeakerMemcachedSessionConfiguration['url'])
    memcached_module = FieldProperty(IBeakerMemcachedSessionConfiguration['memcached_module'])


class BeakerAlchemySessionConfiguration(BeakerSessionConfiguration):
    """Beaker SQLalchemy session configuration"""

    implements(IBeakerAlchemySessionConfiguration)

    configuration = IBeakerAlchemySessionConfiguration

    type = 'ext:sqla'
    url = FieldProperty(IBeakerAlchemySessionConfiguration['url'])
    schema_name = FieldProperty(IBeakerAlchemySessionConfiguration['schema_name'])
    table_name = FieldProperty(IBeakerAlchemySessionConfiguration['table_name'])


class BeakerSessionConfigurationVocabulary(UtilityVocabulary):
    """Beaker session configuration utilities vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IBeakerSessionConfiguration
    nameOnly = True
