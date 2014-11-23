import os
import sys
import getpass
import code

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument
import libtng.db


class Command(BaseCommand):
    command_name = 'shell'
    help_text = "Launches an interactive Python session configured with the Fulcrum environment."
    args = []

    def handle(self, args):
        username = getpass.getuser()
        params = {
            "dbname_prefix": "fulcrum_test"
        }
        dsn = "postgresql+psycopg2://{username}:@localhost/{dbname}".format(
            username=username, dbname="fulcrum_test_{0}".format(username))
        libtng.db.add_connection('default', dsn)
        code.interact(local={'session_factory': libtng.db.get_session})
