from os.path import dirname
from os.path import join
from os.path import abspath
import os
import sys

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument
from libtng.config import Settings
import libtng.db
import libtng.const
import libtng

from fulcrum.services import DatabaseBuildService
from fulcrum import const


def setup_connections(config_filepath):
    settings = Settings.fromfile(config_filepath)
    settings.setup_databases(connections)
    return settings


def get_session(value):
    try:
        return libtng.db.get_session(value)
    except KeyError:
        return None


class Command(BaseCommand):
    command_name = 'renderdb'
    description = "Render the SQL statements to create the TNG Enterprise Management System database."
    args = [
        Argument('--pipe', action='store_true', help="pipe the rendered SQL to stdout."),
        Argument('-f', dest='filename', help="write the rendered SQL to file."),
        Argument('--schema-infrastructure', help="the schema holding infrastructure-specific data.",
            default='data_infra'),
        Argument('--schema-application', help="the schema holding application-specific data.",
            default='data_application'),
        Argument('--schema-domain', help="the schema holding domain-specific data.",
            default='data_domain'),
        Argument('--schema-common', help="the schema holding shared data.",
            default='common'),
        Argument('--schema-history', help="the schema holding the historical state of the database.",
            default='data_history'),
        Argument('--no-remote-data', help='disabled data retrieval from remote sources',
            action='store_true'),
        Argument('--with-example-data', help='insert example data',
            action='store_true'),
        Argument('--settings', type=setup_connections, default=const.FULCRUM_LOCAL_CONFIG,
            help="points to the configuration file holding the database connection settings."),
        Argument('--using', default=libtng.const.DEFAULT_DB_ALIAS, type=get_session, dest='session',
            help="the database connection to use (default: {0})".format(libtng.const.DEFAULT_DB_ALIAS)),
        Argument('-e', action='append', dest='extra_sql_files',
            help="specifies the paths to files containing SQL statements"),
        Argument('-c', action='append', dest='components',
            help="specify the component(s) to render."),
        Argument('-D','--drop', dest='drop', help="drop existing entities.", 
            action='store_true')
    ]

    def handle(self, args):
        params = {
            'schema_infrastructure' : args.schema_infrastructure,
            'schema_application'    : args.schema_application,
            'schema_domain'         : args.schema_domain,
            'schema_common'         : args.schema_common,
            'schema_history'        : args.schema_history,
            'with_remote_data'      : not args.no_remote_data,
            'with_example_data'     : args.with_example_data,
            'libtng_module_dir'     : abspath(join(dirname(libtng.__file__), os.pardir)),
            'with_drop'             : args.drop
        }
        service = DatabaseBuildService(args.session)
        if args.pipe:
            sql = service.render_database_sql(components=args.components,
                template_vars=params)
            print(sql, file=sys.stdout)
        elif args.filename:
            sql = service.render_database_sql(components=args.components,
                template_vars=params)
            with open(args.filename, 'wb') as f:
                f.write(sql)
        elif args.settings:
            if not args.session:
                print(
                    "No database connection could be loaded from the c"
                    "onfiguration file.", file=sys.stderr)
                sys.exit(1)
            service.execute_database_sql(template_vars=params)
        else:
            print(
                "You must instruct the program to pipe to stdout, writ"
                "e to file or execute the rendered SQL using a databas"
                "e connection.", file=sys.stderr)
            sys.exit(1)

