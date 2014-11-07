"""
********************************************************************************
* Name: persistent store
* Author: Nathan Swain
* Created On: September 22, 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import sys

from django.conf import settings
from sqlalchemy import create_engine


class PersistentStore(object):
    """
    An object that stores the data for a Tethys Persistent store
    """

    def __init__(self, name, initializer, postgis=False):
        """
        Constructor
        """
        # Validate
        ## TODO: Validate persistent store object
        self.name = name
        self.initializer = initializer
        self.postgis = postgis

    def __repr__(self):
        """
        String representation
        """
        return '<Persistent Store: name={0}, initializer={1}, postgis={2}>'.format(self.name,
                                                                                   self.initializer,
                                                                                   self.postgis)


def get_persistent_store_engine(app_name, persistent_store_name):
    """
    Returns an sqlalchemy engine for the given store
    """
    # Create the unique store name
    unique_store_name = '_'.join([app_name, persistent_store_name])

    # Get database manager
    database_manager_url = settings.TETHYS_APPS_DATABASE_MANAGER_URL

    # Create connection engine
    engine = create_engine(database_manager_url)
    connection = engine.connect()

    # Check for Database
    existing_dbs_statement = '''
                             SELECT d.datname as name
                             FROM pg_catalog.pg_database d
                             LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
                             ORDER BY 1;
                             '''

    existing_dbs = connection.execute(existing_dbs_statement)

    # Compile list of db names
    existing_db_names = []

    for existing_db in existing_dbs:
        existing_db_names.append(existing_db.name)

    # Check to make sure that the persistent store exists
    if unique_store_name in existing_db_names:
        # Retrieve the database manager url.
        # The database manager database user is the owner of all the app databases.
        database_manager_url = settings.TETHYS_APPS_DATABASE_MANAGER_URL
        url_parts = database_manager_url.split('/')

        # Assemble url for persistent store with that name
        persistent_store_url = '{0}//{1}/{2}'.format(url_parts[0], url_parts[2], unique_store_name)

        # Return SQLAlchemy Engine
        return create_engine(persistent_store_url)

    else:
        print('ERROR: No persistent store "{0}" for app "{1}". Make sure you register the persistent store in app.py '
              'and reinstall app.'.format(persistent_store_name, app_name))
        sys.exit()