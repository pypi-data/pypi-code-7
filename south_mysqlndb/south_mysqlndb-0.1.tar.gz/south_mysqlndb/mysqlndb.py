from __future__ import print_function
try:
    from south.db.mysql import DatabaseOperations as BaseDatabaseOperations
    from south.logger import get_logger
    from south.utils.py3 import text_type
except ImportError:
    print('can not load south')
    raise
try:
    from django.db.utils import DatabaseError
except ImportError:
    print('can not load django')
    raise

MYSQLNDB_SPECIFIC_ERROR = ['Converted FIXED field to DYNAMIC to enable on-line ADD COLUMN']

class DatabaseOperations(BaseDatabaseOperations):

    def execute(self, sql, params=[], print_all_errors=True):
        """
        Executes the given SQL statement, with optional parameters.
        If the instance's debug attribute is True, prints out what it executes.
        """
        
        self._possibly_initialise()
        
        cursor = self._get_connection().cursor()
        if self.debug:
            print("   = %s" % sql, params)

        if self.dry_run:
            return []

        get_logger().debug(text_type('execute "%s" with params "%s"' % (sql, params)))

        try:
            cursor.execute(sql, params)
        except DatabaseError as e:
            if print_all_errors:
                self._print_sql_error(e, sql, params)
            raise
        except Exception as e:
            if str(e) in MYSQLNDB_SPECIFIC_ERROR:
                print('mysqlndb specific warning: %s', e)

        try:
            return cursor.fetchall()
        except:
            return []