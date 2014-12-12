#!/usr/bin/python
"""
Usage: create_tables.py
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This script creates database tables for suprabackup

"""
import sys

from suprabackup import db
from suprabackup.config import load_config

def main():
    """
    Main entry point for create_tables script

    """
    if len(sys.argv) > 1:
        print("Loading config from {}".format(sys.argv[1]))
        config = load_config(path=sys.argv[1])
    else:
        config = load_config()
    engine  = db.get_engine(engine=config['database']['engine'],
                            host=config['database']['host'],
                            db=config['database']['db'],
                            user=config['database']['user'],
                            password=config['database'].get('password', ''),
                        )
    db.Model.metadata.create_all(engine)


if __name__ == "__main__":
    main()
