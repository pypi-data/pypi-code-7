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
    settings = Settings.fromfile(config_filepath, const.LOCAL_CONFIG)
    settings.setup_databases(libtng.db._connections)
    return settings


def get_session(value):
    try:
        return libtng.db.get_session(value)
    except KeyError:
        return None


class Command(BaseCommand):
    command_name = 'renderdb'
    help_text = "Render the SQL statements to create the TNG Enterprise Management System database."
    args = [
        Argument('--pipe', action='store_true', help="pipe the rendered SQL to stdout."),
        Argument('-f', dest='filename', help="write the rendered SQL to file."),
        Argument('--schema-common', help="the schema holding shared data.",
            default=const.SCHEMA_COMMON),
        Argument('--no-remote-data', help='disabled data retrieval from remote sources',
            action='store_true'),
        Argument('--with-example-data', help='insert example data',
            action='store_true'),
        Argument('-e', action='append', dest='extra_sql_files',
            help="specifies the paths to files containing SQL statements"),
        Argument('-c', action='append', dest='components',
            help="specify the component(s) to render."),
        Argument('--config-file', default=const.GLOBAL_CONFIG, dest='settings',
            type=setup_connections),
        Argument('-D','--drop', dest='drop', help="drop existing entities.",
            action='store_true'),
        Argument('--using', help="specifies the database alias to use."),
        Argument('--debug', action='store_true', help="enable debug statements")
    ]

    def handle(self, args):
        params = {
            'schema_common'         : args.schema_common,
            'with_remote_data'      : not args.no_remote_data,
            'with_example_data'     : args.with_example_data,
            'libtng_module_dir'     : abspath(join(dirname(libtng.__file__), os.pardir)),
            'with_drop'             : args.drop,
            'DEBUG'                 : args.debug
        }
        service = DatabaseBuildService(get_session(args.using))
        if args.pipe:
            sql = service.render_database_sql(components=args.components,
                template_vars=params)
            print(sql, file=sys.stdout)
        elif args.filename:
            sql = service.render_database_sql(components=args.components,
                template_vars=params)
            with open(args.filename, 'wb') as f:
                f.write(sql)
        elif getattr(args, 'using', None):
            service.execute_database_sql(template_vars=params)
        else:
            print(
                "You must instruct the program to pipe to stdout, writ"
                "e to file or execute the rendered SQL using a databas"
                "e connection.", file=sys.stderr)
            sys.exit(1)

