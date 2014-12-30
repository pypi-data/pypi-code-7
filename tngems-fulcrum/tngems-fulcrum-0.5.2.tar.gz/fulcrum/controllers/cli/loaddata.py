from os.path import normpath
from os.path import expanduser
from os.path import abspath
from os.path import exists
import code
import sys

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument
from libtng.module_loading import import_string
import libtng.db

from fulcrum.serializer import Serializer
from fulcrum.services import DatasetImportService
from fulcrum.settings import Settings
import fulcrum.const


LOADERS = [
    'fulcrum.loaders.impl.PrincipalLoader'
]
LOADERS = map(import_string, LOADERS)


class Command(BaseCommand):
    command_name = 'loaddata'
    help_text = (
        "Various utilities to import datasets into the Fulcrum MDM"
    )
    args = [
        Argument('--config-file', type=Settings.fromfile, dest='settings',
            help="specifies the configuration file to use (default: {0})."\
                .format(fulcrum.const.GLOBAL_CONFIG),
            default=fulcrum.const.GLOBAL_CONFIG),
        Argument('-f', dest="files", default=[], action='append',
            help="specifies the files to load into the MDM."),
        Argument('--using', default='master', type=str,
            help="specifies the database connection to use.")
    ]

    def normalize_file(self, filename):
        if filename.startswith('~'):
            filename = expanduser(filename)
        return normpath(abspath(filename))

    def handle(self, args):
        args.settings.setup_databases(libtng.db._connections)
        if not args.files:
            print("Specify at least one file", file=sys.stderr)
            sys.exit(1)
        files = list(map(self.normalize_file, args.files))
        for src in files:
            if not exists(src):
                print("No such file: {0}".format(src), file=sys.stderr)
                sys.exit(1)

        session = libtng.db.get_session(args.using)
        session.bind.echo = True
        service = DatasetImportService(Serializer(), session,
            loaders=[x(session) for x in list(LOADERS)])
        service.load_many(files)

