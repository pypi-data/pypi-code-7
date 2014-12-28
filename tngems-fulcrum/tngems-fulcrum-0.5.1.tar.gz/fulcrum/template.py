from os.path import abspath
from os.path import dirname
from os.path import join
import os
import copy

import libtng
import libsovereign.const

from fulcrum import const


default_params = {
    'DEBUG'                         : False,
    'TNGEMS_OBJECT_SEQUENCE'        : 'tngems_object_id_seq',
    'schema_public'                 : const.SCHEMA_PUBLIC,
    'schema_common'                 : const.SCHEMA_COMMON,
    'schema_system'                 : const.SCHEMA_SYSTEM,
    'schema_entities'               : const.SCHEMA_ENTITIES,
    'schema_state'                  : const.SCHEMA_STATE,
    'with_remote_data'              : True,
    'with_example_data'             : False,
    'libtng_module_dir'             : abspath(join(dirname(libtng.__file__), os.pardir)),
    'with_drop'                     : False,
    'with_data'                     : True,
    'with_history_drop'             : False,
    'with_remote_data'              : True,
    'drop_cascade'                  : False,
    'initdb'                        : False,
    'DEBUG'                         : False,
    'cross_schema_references'       : True,
    'TNGEMS_UNSPECIFIED_PARTY_ID'   : libsovereign.const.UNSPECIFIED_PARTY_ID
}


def get_default_context():
    return copy.deepcopy(default_params)
