from os.path import expanduser
from os.path import normpath
from os.path import abspath
from os.path import join
import sys
import getpass

try:
    from libtng.const import SCHEMA_MASTER
    from libtng.const import SCHEMA_DOMAIN
    from libtng.const import SCHEMA_ARCHITECTURE
    from libtng.const import SCHEMA_HISTORY
    from libtng.const import SCHEMA_PUBLIC
    from libtng.const import SCHEMA_VIRTUAL
    from libtng.const import SCHEMA_APPLICATION
    from libtng.const import SCHEMA_INFRASTRUCTURE
    from libtng.const import SCHEMA_COMMON
    from libtng.const import SCHEMA_PG_CATALOG
    from libtng.const import SCHEMA_PHALANX
    from libtng.const import SCHEMA_CFS
    from libtng.const import SCHEMA_HC
    from libtng.const import DEFAULT_USER_ID
    from libtng.const import DEFAULT_CLIENT_ID
except ImportError:
    # TODO: This is a dirty hack to prevent pip from failing to
    # install fulcrum if libtng is not installed yet.
    pass

#//////////////////////////////////////////////////////////////////////
#// General
#//////////////////////////////////////////////////////////////////////
TG_SHARED_DIR = '/usr/share/fulcrum'

#: Directory holding Fulcrum shared files.
FULCRUM_SHARED_DIR = join(sys.prefix, 'share/fulcrum')


#: The system-wide Fulcrum configuration file.
FULCRUM_GLOBAL_CONFIG   = '/etc/fulcrum/fulcrum.conf'


#: The user-specific Fulcrum configuration file.
FULCRUM_LOCAL_CONFIG    = normpath(expanduser('~/.fulcrum'))


#: Specifies the directory holding the exported domain types.
DOMAIN_TYPES_DATA_DIR = join(FULCRUM_SHARED_DIR, 'types')


#: Holds system data.
SCHEMA_SYSTEM = 'data_system'


#//////////////////////////////////////////////////////////////////////
#// Database connections
#//////////////////////////////////////////////////////////////////////

#: Default database alias
DEFAULT_DB_ALIAS = 'default'



TEST_POSTGRES_DB = "test_fulcrum_" + getpass.getuser()
TEST_POSTGRES_DSN = "postgresql+psycopg2:///{0}".format(TEST_POSTGRES_DB)
