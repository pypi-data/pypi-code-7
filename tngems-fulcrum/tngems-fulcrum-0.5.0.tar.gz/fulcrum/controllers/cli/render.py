from os.path import normpath
from os.path import expanduser
from os.path import abspath
from os.path import exists
from os.path import join
from os.path import dirname
import os
import sys

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument
from libtng.config import Settings
import libtng.const
import libtng
import jinja2

from fulcrum import const
import fulcrum.template


class Command(BaseCommand):
    command_name = 'render'
    help_text = "Renders SQL templates with the Fulcrum environment."
    args = [
        Argument('dst', 
            help="specifies the location of the output file. Use '-' for stdout."),
        Argument('-f', dest='files', action='append', default=[],
            help="specifies one or more files to render."),
        Argument('--schema-common', help="the schema holding shared data.",
            default=const.SCHEMA_COMMON),
        Argument('--debug', action='store_true', help="enable debug statements"),
        Argument('--with-init', action='store_true',
            help="include the Fulcrum database initialization script."),
        Argument('--with-drop', dest='drop', action='store_true',
            help="adds DROP statements to the rendered SQL.")
    ]

    def normalize_file(self, filename):
        if filename.startswith('~'):
            filename = expanduser(filename)
        return normpath(abspath(filename))
    
    def get_files(self, args):
        if not args.files:
            print("Specify at least one file", file=sys.stderr)
            sys.exit(1)
        files = list(map(self.normalize_file, args.files))
        for src in files:
            if not exists(src):
                print("No such file: {0}".format(src), file=sys.stderr)
                sys.exit(1)
        return files

    def write_to_file(self, dst, sql):
        if dst == '-':
            print(sql, file=sys.stdout)
            sys.exit(0)
        with open(self.normalize_file(dst), 'w') as f:
            f.write(sql + chr(10))

    def get_template(self, src):
        return jinja2.Template(open(src).read())

    def handle(self, args):
        params = {
            'schema_common'         : args.schema_common,
            'libtng_module_dir'     : abspath(join(dirname(libtng.__file__), os.pardir)),
            'with_drop'             : args.drop,
            'DEBUG'                 : args.debug
        }
        files = self.get_files(args)
        context = fulcrum.template.get_default_context()
        context.update(params)
        sql = ''
        if args.with_init:
            template = jinja2.Template(
                open(join(const.FULCRUM_SHARED_DIR, 'templates/sql/initdb.sql.j2')).read())
            sql += template.render(**context)
        for filename in files:
            template = self.get_template(filename)
            sql += template.render(**context)
        self.write_to_file(args.dst, sql)

