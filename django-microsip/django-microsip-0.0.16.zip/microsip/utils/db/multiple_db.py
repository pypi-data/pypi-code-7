import os
import fdb

class ConnectionDatabases(dict):
    ''' Objeto guardar las conexiones a las bases de datos. '''
    connections = []  
    def __init__(self,):
        self.connections = self.get_connections()
        for connection in self.connections:
            self.add_database_connections(connection)

    def add_database(connection, database_name):
        try:
            if database_name == 'CONFIG':
                connection.path = '%s\System'% connection.path
            database_name = '%s\%s.FDB'% (connection.path, database_name)
        except UnicodeDecodeError:
            pass

        database_id = '%s-CONFIG'%connection.id

        self[database_id] = {
            'ENGINE':'firebird',
            'NAME': database_name,
            'PORT': '3050',
            'OPTIONS': {'charset':'ISO8859_1'},
            'USER': connection.user,
            'PASSWORD': connection.password,
            'HOST': connection.host,
        }   


    def get_connections(**kwargs):
        """
        Return data bases connections added to configuration
        """


        return []

    def get_connection_databases(connection):
        """
        Get connection databases
        """
        empresas = []
        try:
            db= fdb.connect(host=connection.host, user=connection.user, password=connection.password, database="%s\System\CONFIG.FDB"%connection.path )
        except fdb.DatabaseError:
            pass
        else:
            cur = db.cursor()
            cur.execute("SELECT NOMBRE_CORTO FROM EMPRESAS")
            empresas = cur.fetchall()
            db.close()

        return empresas

    def add_database_connections(connection):
        """
        add database connections to the object
        """
        empresas = self.get_connection_databases(connection)
        if empresas:
            self.add_database(connection,'CONFIG')
            for empresa in empresas:                
                self.add_database(connection,empresa[0])