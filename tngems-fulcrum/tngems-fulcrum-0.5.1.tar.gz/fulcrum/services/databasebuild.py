from os.path import join, dirname, abspath
import itertools
import copy
import os

from sqlalchemy.schema import DDL
from libtng.services import DatabaseMixin
from libtng import template
from libtng import timezone
import libtng

from fulcrum.template import get_default_context
from fulcrum import const


class DatabaseBuildService(DatabaseMixin):
    default_params = {
        'TNGEMS_OBJECT_SEQUENCE'    : 'tngems_object_id_seq',
        'schema_public'             : const.SCHEMA_PUBLIC,
        'schema_common'             : const.SCHEMA_COMMON,
        'schema_system'             : const.SCHEMA_SYSTEM,
        'schema_entities'           : const.SCHEMA_ENTITIES,
        'schema_state'              : const.SCHEMA_STATE,
        'with_remote_data'          : True,
        'with_example_data'         : False,
        'libtng_module_dir'         : abspath(join(dirname(libtng.__file__), os.pardir)),
        'with_drop'                 : False,
        'with_data'                 : True,
        'with_history_drop'         : False,
        'with_remote_data'          : True,
        'drop_cascade'              : False,
        'initdb'                    : False,
        'DEBUG'                     : False,
        'cross_schema_references'   : True
    }

    database_components = [
        'system',
        'uom',
        'locale',
        'iso',
        'vat',
        'uom',
        'tld',
        'dns',

        # Infrastructure domains
        'auth',
        'storage',
        #'zone',
        #'web',

        # Business domains
        'contact',
        'party',
        #'contributor',
        #'crm',
        #'stash',
        'product',
        'payment'
    ]
    filename_order = ['types.sql.j2','ddl.sql.j2','history.sql.j2',
        'procedures.sql.j2','virtual.sql.j2','triggers.sql.j2',
        'initial_data.sql.j2']
    template_search_dirs = [
        const.FULCRUM_SHARED_DIR, 
        const.TG_SHARED_DIR, 
        join(const.FULCRUM_SHARED_DIR, 'templates/sql')
    ]


    def __init__(self, session, default_params=None, search_dirs=None):
        self._session = session
        self.default_params.update(default_params or {})
        search_dirs = search_dirs or []
        search_dirs.extend(self.template_search_dirs)
        template.configure(template_dirs=search_dirs, autoescape=False)
        template.initialize()

    def render_database_sql(self, components=None, template_vars=None):
        """
        Output a string containing the Structured Query Language (SQL)
        statements to create the Fulcrum database.

        Args:
            components (list): a list specifying the components to
                include in the rendered SQL. Default is None, meaning
                that all components are included.
            template_vars (dict): holds variables to be included in the
                template engine.

        Returns:
            str
        """
        sql = []
        context_dict = get_default_context()
        context_dict.update(template_vars or {})
        context_dict['generated'] = timezone.now()
        for t in self._get_template_instances(components=components):
            sql.append(t.render(context_dict))
        return 'BEGIN;\n' + '\n\n\n'.join(sql) + '\n\n\nCOMMIT;'

    def execute_database_sql(self, components=None, template_vars=None):
        """
        Compiles the database and opens a connection to execute the
        compiled SQL statements.

        Args:
            components (list): a list specifying the components to
                include in the rendered SQL. Default is None, meaning
                that all components are included.
            template_vars (dict): holds variables to be included in the
                template engine.
        """
        assert self._session is not None, (
            "Provide a database session to the service contructor.")
        ddl = self.render_database_sql(components=components,
            template_vars=template_vars)
        self._session.connection().execute(ddl)


    def _get_template_instances(self, components=None):
        for x in self._find_components_sql(schemata=components):
            try:
                yield template.get_template(x)
            except template.TemplateDoesNotExist:
                continue

    def _find_components_sql(self, schemata=None):
        """
        Finds the SQL for all specified TNGEMS components.
        """
        schemata = list(copy.deepcopy(schemata or self.database_components))
        if 'system' not in schemata:
            schemata.insert(0, 'system')
        base_dir = 'templates/sql'
        sql = [join(base_dir, 'initdb.sql.j2')]
        for schema, filename in itertools.product(schemata, self.filename_order):
            src = join(base_dir, schema, filename)
            sql.append(src)
        sql.append(join(base_dir, 'closure.sql'))
        return sql




