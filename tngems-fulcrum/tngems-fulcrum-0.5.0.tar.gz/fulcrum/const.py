from os.path import expanduser
from os.path import normpath
from os.path import abspath
from os.path import join
import sys
import getpass

import libsovereign.const


try:
    from libtng.const import SCHEMA_PUBLIC
    from libtng.const import SCHEMA_COMMON
    from libtng.const import DEFAULT_USER_ID
    from libtng.const import DEFAULT_CLIENT_ID
except ImportError:
    # TODO: This is a dirty hack to prevent pip from failing to
    # install fulcrum if libtng is not installed yet.
    pass

#//////////////////////////////////////////////////////////////////////
#// General
#//////////////////////////////////////////////////////////////////////

#: The base directory for Fulcrum configuration files.
CONF_DIR = join(libsovereign.const.CONF_DIR, 'components', 'fulcrum')

#: The global Fulcrum configuration file.
GLOBAL_CONFIG = join(CONF_DIR, 'fulcrum.conf')

#: Local, user specific config file.
LOCAL_CONFIG = '~/.fulcrum'

TG_SHARED_DIR = '/usr/share/tngems/fulcrum'

#: Directory holding Fulcrum shared files.
FULCRUM_SHARED_DIR = TG_SHARED_DIR

#: The user-specific Fulcrum configuration file.
FULCRUM_LOCAL_CONFIG    = normpath(expanduser('~/.fulcrum'))

#: The database schema holding private system states and configurations.
SCHEMA_SYSTEM = 'system'

#: Specifies the name of the database schema holding the lookup tables
#: shared by all TNGEMS subsystems.
SCHEMA_COMMON = "common"

#: Specifies the name of the database schema declaring the relations
#: of the domain entities.
SCHEMA_ENTITIES = "entities"

#: Specifies the name of the database schema holding the state of the
#: domain entities.
SCHEMA_STATE = "state"

#//////////////////////////////////////////////////////////////////////
#// Database connections
#//////////////////////////////////////////////////////////////////////

#: Default database alias
DEFAULT_DB_ALIAS = 'default'



TEST_POSTGRES_DB = "test_fulcrum_" + getpass.getuser()
TEST_POSTGRES_DSN = "postgresql+psycopg2:///{0}".format(TEST_POSTGRES_DB)
