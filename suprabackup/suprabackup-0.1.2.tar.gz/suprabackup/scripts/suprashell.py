#!/usr/bin/python
"""
Usage: suprashell.py [config]
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This script gives a shell to Suprabackup database using the ORM

"""
import os
import sys

from code import InteractiveConsole

from suprabackup import db
from suprabackup.config import load_config
from suprabackup.models import *

motd = """
###############################
### Welcome to Suprashell ! ###
###############################

Use quit() or ^D to Exit

Available resources are:
 - session: An handler to a SQLAlchemy session
 - config: A SupraConfig dictionary
"""

def main():
    if len(sys.argv) > 1:
        config = load_config(path=sys.argv[1])
    else:
        config = load_config()
    print("Loaded config from {}".format(config.file))
    session = db.connect(engine=config['database']['engine'],
                            host=config['database']['host'],
                            db=config['database']['db'],
                            user=config['database']['user'],
                            password=config['database'].get('password', ''),
                        )
    vars = {'session': session, 'config': config}
    console = InteractiveConsole(vars)
    console.interact(banner=motd)

if __name__ == "__main__":
    main()
