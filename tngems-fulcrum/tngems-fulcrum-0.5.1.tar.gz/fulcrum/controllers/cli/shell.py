import code

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument
import libtng.db

from fulcrum.settings import Settings
import fulcrum.const


class Command(BaseCommand):
    command_name = 'shell'
    help_text = (
        "Launches an interactive Python shell configured with the Fulcrum en"\
        "vironment."
    )
    args = [
        Argument('--config-file', type=Settings.fromfile, dest='settings',
            help="specifies the configuration file to use (default: {0})."\
                .format(fulcrum.const.GLOBAL_CONFIG),
            default=fulcrum.const.GLOBAL_CONFIG)
    ]

    def get_locals(self, args):
        args.settings.setup_databases(libtng.db._connections)
        return {
            'const': fulcrum.const,
            'settings': args.settings,
            'get_session': libtng.db.get_session
        }

    def handle(self, args):
        code.interact(local=self.get_locals(args))
