#coding:utf8

"""
Created on 2014-05-19

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import logging
import threading
import functools
from DBUtils.PooledDB import PooledDB

logger = logging.getLogger("database")


class DatabaseError(Exception):
    """数据库访问异常
    """


class TransactionError(DatabaseError):
    """数据库事务异常
    """


class ConnectionFactory(object):
    """
    """

    __conn_dict = dict()

    __pool = None

    @classmethod
    def set_pool(cls, pool):
        if isinstance(pool, PooledDB):
            cls.__pool = pool
        else:
            raise DatabaseError("Invalid Pool instance, must be DBUtils.PooledDB")

    @classmethod
    def get(cls):
        current_thd_name = threading.currentThread().getName()
        if cls.__conn_dict.has_key(current_thd_name):
            return cls.__conn_dict.get(current_thd_name)
        else:
            if cls.__pool is None:
                raise DatabaseError("Please call set_pool() first.")
            # Only support Mysql
            conn = MySQLConnection(cls.__pool)
            cls.__conn_dict[current_thd_name] = conn
            return conn


class Connection(object):

    def __init__(self, connection_pool=None):
        self.__db = None
        self.__pool = connection_pool

    def connect(self):
        raise NotImplementedError()

    def get_connection(self):
        if self.__db is None:
            if self.__pool is not None:
                self.__db = self.__pool.connection()
            else:
                self.__db = self.connect()
        return self.__db

    def close(self):
        if self.__db is not None:
            self.__db.close()
            self.__db = None

    def commit(self):
        if self.in_transaction():
            self.get_connection().commit()

    def rollback(self):
        if self.in_transaction():
            self.get_connection().rollback()

    def in_transaction(self):
        raise NotImplementedError()

    def fmt_exception(self, e):
        raise NotImplementedError


class MySQLConnection(Connection):

    def __init__(self, connection_pool=None, username=None, password=None, hostname=None, db=None):
        Connection.__init__(self, connection_pool)
        self.username = username
        self.password = password
        self.hostname = hostname
        self.db = db

    def connect(self):
        import MySQLdb
        return MySQLdb.connect(self.hostname, self.username, self.password, self.db)

    def in_transaction(self):
        return True

    def fmt_exception(self, e):
        import MySQLdb
        if isinstance(e, MySQLdb.Error):
            return "MySQLdb Error %d: %s" % (e.args[0], e.args[1])
        return e.message


class OracleConnection(Connection):

    def __init__(self, connection_pool=None, username=None, password=None, hostname=None, db=None):
        Connection.__init__(self, connection_pool)
        self.username = username
        self.password = password
        self.hostname = hostname
        self.db = db

    def connect(self):
        import cx_Oracle
        return cx_Oracle.connect(self.username, self.password, self.db)


class RowMapper(object):
    """
    This is an interface to handle one row of data.
    """
    def map_row(self, row, metadata):
        raise NotImplementedError()


class DictionaryRowMapper(RowMapper):
    """
    This row mapper converts the tuple into a dictionary using the column names as the keys.
    """
    def map_row(self, row, metadata):
        obj = {}
        for i, column in enumerate(metadata):
            obj[column["name"]] = row[i]
        return obj


class SimpleRowMapper(RowMapper):
    """
    This row mapper uses convention over configuration to create and populate attributes
    of an object.
    """
    def __init__(self, clazz):
        self.clazz = clazz

    def map_row(self, row, metadata):
        obj = self.clazz()
        for i, column in enumerate(metadata):
            setattr(obj, column["name"], row[i])
        return obj


class DatabaseTemplate(object):

    def __init__(self, connection=None):
        self.connection = connection

    def __del__(self):
        """When this template goes out of scope, need to close the connection it formed.
        """
        if self.connection is not None:
            self.connection.close()

    def _execute(self, sql_statement, params=None):
        cursor = self.connection.get_connection().cursor()
        try:
            logger.debug("sql:[%s], params:[%s]" % (sql_statement, params))
            if params:
                cursor.execute(sql_statement, params)
            else:
                cursor.execute(sql_statement)
            rowcount = cursor.rowcount
            lastrowid = cursor.lastrowid

            return [rowcount, lastrowid]
        except Exception, e:
            logger.exception("database execute error. sql:[%s], params:[%s]" % (sql_statement, params))
            raise DatabaseError(self.connection.fmt_exception(e))
        finally:
            try:
                cursor.close()
            except Exception, e:
                logger.debug("release database connction error: %s" % e.message)

    def execute(self, sql_statement, params=None):
        return self._execute(sql_statement, params)[0]

    def insert(self, sql_statement, params=None):
        return self._execute(sql_statement, params)[1]

    def update(self, sql_statement, params=None):
        return self.execute(sql_statement, params)

    def query(self, sql_statement, params=None, row_mapper=None):

        def get_metadata(desc_row):
            return {"name": desc_row[0],
                    "type_code": desc_row[1],
                    "display_size": desc_row[2],
                    "internal_size": desc_row[3],
                    "precision": desc_row[4],
                    "scale": desc_row[5],
                    "null_ok": desc_row[6]}

        cursor = self.connection.get_connection().cursor()
        try:
            logger.debug("sql:[%s], params:[%s]" % (sql_statement, params))
            if params:
                cursor.execute(sql_statement, params)
            else:
                cursor.execute(sql_statement)
            rs = cursor.fetchall()
            if rs:
                if not row_mapper:
                    row_mapper = DictionaryRowMapper()
                metadata = [get_metadata(row) for row in cursor.description]
                return [row_mapper.map_row(row, metadata) for row in rs]
            else:
                return []
        except Exception, e:
            logger.exception("database query error. sql:[%s], params:[%s]" % (sql_statement, params))
            raise DatabaseError(self.connection.fmt_exception(e))
        finally:
            try:
                cursor.close()
            except Exception, e:
                logger.debug("release database connection error: %s" % e.message)

    def get(self, sql_statement, params=None, row_mapper=None):
        rs = self.query(sql_statement, params, row_mapper)
        return rs[0] if rs else None


class TransactionStatus(object):
    pass


class TransactionDefinition(object):

    def __init__(self, isolation, name, propagation, timeout, read_only):
        self.isolation = isolation
        self.name = name
        self.propagation = propagation
        self.timeout = timeout
        self.read_only = read_only


class DefaultTransactionDefinition(TransactionDefinition):

    def __init__(self):
        super(DefaultTransactionDefinition, self).__init__("ISOLATION_DEFAULT", "",
                                                           "PROPAGATION_REQUIRED", "TIMEOUT_DEFAULT", False)


class TransactionTemplate(DefaultTransactionDefinition):
    """This utility class is used to simplify defining transactional blocks.
    Any exceptions thrown inside the transaction block will be propagated to whom ever
    is calling the template execute method.
    """

    def __init__(self, tx_manager):
        super(TransactionTemplate, self).__init__()
        self.tx_manager = tx_manager

    def execute(self, transaction_cb):
        """Execute the action specified by the given callback object within a transaction.
        """

        status = self.tx_manager.get_transaction(self)
        try:
            logger.debug("Execute the steps inside the transaction")
            result = transaction_cb.do_in_transaction(status)
            self.tx_manager.commit(status)
            return result
        except Exception, e:
            logger.debug("Transaction Exception: (%s)" % e.message)
            self.tx_manager.rollback(status)
            raise e

    def set_tx_attributes(self, tx_attributes):
        for tx_def_prop in tx_attributes:
            if tx_def_prop.startswith("ISOLATION"):
                if tx_def_prop != self.isolation:
                    self.isolation = tx_def_prop
            elif tx_def_prop.startswith("PROPAGATION"):
                if tx_def_prop != self.propagation:
                    self.propagation = tx_def_prop
            elif tx_def_prop.startswith("TIMEOUT"):
                if tx_def_prop != self.timeout:
                    self.timeout = tx_def_prop
            elif tx_def_prop == "read_only":
                if not self.read_only:
                    self.read_only = True
            else:
                logger.debug("Don't know how to handle %s" % tx_def_prop)


class TransactionManager(object):

    def __init__(self, connection):
        self.connection = connection
        self.status = []

    def get_transaction(self, definition):
        start_tx = False

        if definition.propagation == "PROPAGATION_REQUIRED":
            if len(self.status) == 0:
                logger.debug("There is no current transaction, and one is required, so starting one.")
                start_tx = True
            self.status.append(TransactionStatus())
        elif definition.propagation == "PROPAGATION_SUPPORTS":
            logger.debug("This code can execute inside or outside a transaction.")
        elif definition.propagation == "PROPAGATION_MANDATORY":
            if len(self.status) == 0:
                raise TransactionError("Trying to execute PROPAGATION_MANDATORY operation while outside TX")
            self.status.append(TransactionStatus())
        elif definition.propagation == "PROPAGATION_NEVER":
            if len(self.status) != 0:
                raise TransactionError("Trying to execute PROPAGATION_NEVER operation while inside TX")
        else:
            raise TransactionError("Transaction propagation level %s is not supported!" % definition.start_tx)

        if start_tx:
            logger.debug("START TRANSACTION")
            logger.debug("Creating a transaction, propagation = %s, isolation = %s, timeout = %s, read_only = %s"
                           % (definition.propagation, definition.isolation, definition.timeout, definition.read_only))
            self.connection.commit()

        return self.status

    def commit(self, status):
        self.status = status
        try:
            self.status.pop()
            if len(self.status) == 0:
                logger.debug("Commit the changes")
                self.connection.commit()
                logger.debug("END TRANSACTION")
        except IndexError:
            pass

    def rollback(self, status):
        self.status = status
        try:
            self.status.pop()
            if len(self.status) == 0:
                logger.debug("Rolling back the transaction.")
                self.connection.rollback()
                logger.debug("END TRANSACTION")
        except IndexError:
            pass


class TransactionCallback(object):
    """This interface defines the basic action needed to plug into the TransactionTemplate
    """

    def do_in_transaction(self, status):
        raise NotImplementedError()


def transactional(tx_attributes=None):

    def _transactional(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            class TxDef(TransactionCallback):

                def do_in_transaction(self, status):
                    return func(*args, **kwargs)

            try:
                tx_manager = TransactionManager(ConnectionFactory.get())
                tx_template = TransactionTemplate(tx_manager)
                if tx_attributes is not None:
                    tx_template.set_tx_attributes(tx_attributes)
                return tx_template.execute(TxDef())
            except NameError:
                return TxDef().do_in_transaction(None)

        return wrapper

    return _transactional