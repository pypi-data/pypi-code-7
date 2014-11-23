import os
import sys

from libtng.cli.command import BaseCommand
from libtng.cli.argument import Argument

class Command(BaseCommand):
    command_name = 'dbshell'
    args = []

    def handle(self, args):
        params = {
            "dbname_prefix": "fulcrum_test"
        }
        os.system("psql -d {dbname_prefix}_`whoami`".format(**params))
