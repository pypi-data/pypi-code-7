#coding:utf-8
#
#   PROGRAM:     fdb
#   MODULE:      monitor.py
#   DESCRIPTION: Database monitoring
#   CREATED:     10.5.2013
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2013 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

import sys
import os
import fdb
from fdb.utils import LateBindingProperty
import weakref

# Current shutdown mode
SHUTDOWN_MODE_ONLINE = 0
SHUTDOWN_MODE_MULTI = 1
SHUTDOWN_MODE_SINGLE = 2
SHUTDOWN_MODE_FULL = 3

# Current physical backup state
BACKUP_STATE_NORMAL = 0
BACKUP_STATE_STALLED = 1
BACKUP_STATE_MERGE = 2

# State
STATE_IDLE = 0
STATE_ACTIVE = 1

# Flags
FLAG_NOT_SET = 0
FLAG_SET = 1

# Transaction solation mode
ISOLATION_CONSISTENCY = 0
ISOLATION_CONCURRENCY = 1
ISOLATION_READ_COMMITTED_RV = 2
ISOLATION_READ_COMMITTED_NO_RV = 3

# Wait mode
INFINITE_WAIT = -1
NO_WAIT = 0

# Statistics group
STAT_DATABASE = 0
STAT_ATTACHMENT = 1
STAT_TRANSACTION = 2
STAT_STATEMENT = 3
STAT_CALL = 4

class Monitor(object):
    """Class for access to Firebird monitoring tables.
    """
    def __init__(self):
        self._con = None
        self._ic = None
        self.__internal = False
    def __del__(self):
        if not self.closed:
            self._close()
    def __get_closed(self):
        return self._con is None
    def __fail_if_closed(self):
        if self.closed:
            raise fdb.ProgrammingError("Monitor is not binded to connection.")
    def _close(self):
        self._ic.close()
        self._con = None
        self._ic = None
    def _set_as_internal(self):
        """Mark this instance as `internal` (embedded). This blocks calls to 
        :meth:`bind` and :meth:`close`."""
        self.__internal = True
        self._con = weakref.proxy(self._con)
        
        #--- protected

    def _get_database(self):
        if self.__database is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("select * from mon$database")
                self.__database = DatabaseInfo(self,self._ic.fetchonemap())
            else:
                self.__database = []
        return self.__database
    def _get_attachments(self):
        if self.__attachments is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("select * from mon$attachments")
                self.__attachments = [AttachmentInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__attachments = []
        return self.__attachments
    def _get_this_attachment(self):
        return self.get_attachment(self._con.db_info(fdb.isc_info_attachment_id))
    def _get_transactions(self):
        if self.__transactions is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("select * from mon$transactions")
                self.__transactions = [TransactionInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__transactions = []
        return self.__transactions
    def _get_statements(self):
        if self.__statements is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("select * from mon$statements")
                self.__statements = [StatementInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__statements = []
        return self.__statements
    def _get_callstack(self):
        if self.__callstack is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("select * from mon$call_stack")
                self.__callstack = [CallStackInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__callstack = []
        return self.__callstack
    def _get_iostats(self):
        if self.__iostats is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_25:
                self._ic.execute("""SELECT r.MON$STAT_ID, r.MON$STAT_GROUP, 
r.MON$RECORD_SEQ_READS, r.MON$RECORD_IDX_READS, r.MON$RECORD_INSERTS, 
r.MON$RECORD_UPDATES, r.MON$RECORD_DELETES, r.MON$RECORD_BACKOUTS, 
r.MON$RECORD_PURGES, r.MON$RECORD_EXPUNGES, io.MON$PAGE_FETCHES, 
io.MON$PAGE_MARKS, io.MON$PAGE_READS, io.MON$PAGE_WRITES, m.MON$MEMORY_ALLOCATED, 
m.MON$MEMORY_USED, m.MON$MAX_MEMORY_ALLOCATED, m.MON$MAX_MEMORY_USED
FROM MON$RECORD_STATS r join MON$IO_STATS io
  on r.MON$STAT_ID = io.MON$STAT_ID and r.MON$STAT_GROUP = io.MON$STAT_GROUP
  join MON$MEMORY_USAGE m
  on r.MON$STAT_ID = m.MON$STAT_ID and r.MON$STAT_GROUP = m.MON$STAT_GROUP""")
            elif self._con.ods >= fdb.ODS_FB_21:
                self._ic.execute("""SELECT r.MON$STAT_ID, r.MON$STAT_GROUP, 
r.MON$RECORD_SEQ_READS, r.MON$RECORD_IDX_READS, r.MON$RECORD_INSERTS, 
r.MON$RECORD_UPDATES, r.MON$RECORD_DELETES, r.MON$RECORD_BACKOUTS, 
r.MON$RECORD_PURGES, r.MON$RECORD_EXPUNGES, io.MON$PAGE_FETCHES, 
io.MON$PAGE_MARKS, io.MON$PAGE_READS, io.MON$PAGE_WRITES
FROM MON$RECORD_STATS r join MON$IO_STATS io
on r.MON$STAT_ID = io.MON$STAT_ID and r.MON$STAT_GROUP = io.MON$STAT_GROUP""")
            if self._con.ods >= fdb.ODS_FB_21:
                self.__iostats = [IOStatsInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__iostats = []
        return self.__iostats
    def _get_variables(self):
        if self.__variables is None:
            self.__fail_if_closed()
            if self._con.ods >= fdb.ODS_FB_25:
                self._ic.execute("select * from mon$context_variables")
                self.__variables = [ContextVariableInfo(self,row) for row in self._ic.itermap()]
            else:
                self.__variables = []
        return self.__variables

    #--- Properties

    #: True if link to :class:`~fdb.Connection` is closed.
    closed = property(__get_closed)
    db = LateBindingProperty(_get_database,None,None,
        ":class:`DatabaseInfo` object for attached database.")
    attachments = LateBindingProperty(_get_attachments,None,None,
        "List of all attachments.\nItems are :class:`AttachmentInfo` objects.")
    this_attachment = LateBindingProperty(_get_this_attachment,None,None,
        ":class:`AttachmentInfo` object for current connection.")
    transactions = LateBindingProperty(_get_transactions,None,None,
        "List of all transactions.\nItems are :class:`TransactionInfo` objects.")
    statements = LateBindingProperty(_get_statements,None,None,
        "List of all statements.\nItems are :class:`StatementInfo` objects.")
    callstack = LateBindingProperty(_get_callstack,None,None,
        "List with complete call stack.\nItems are :class:`CallStackInfo` objects.")
    iostats = LateBindingProperty(_get_iostats,None,None,
        "List of all I/O statistics.\nItems are :class:`IOStatsInfo` objects.")
    variables = LateBindingProperty(_get_variables,None,None,
        "List of all context variables.\nItems are :class:`ContextVariableInfo` objects.")

    #--- Public

    def bind(self, connection):
        """Bind this instance to specified :class:`~fdb.Connection`.
        
        :param connection: :class:`~fdb.Connection` instance. 
        
        :raises ProgrammingError: If Monitor object was set as internal (via 
            :meth:`_set_as_internal`) or database has ODS lower than 11.1.
        """
        if self.__internal:
            raise fdb.ProgrammingError("Call to 'bind' not allowed for embedded Monitor.")
        if self._con:
            self.close()
        if connection.ods < fdb.ODS_FB_21:
            raise fdb.ProgrammingError("Monitoring tables are available only " \
                                       "for databases with ODS 11.1 and higher.")
        self._con = connection
        self._ic = self._con.trans(fdb.ISOLATION_LEVEL_READ_COMMITED_RO).cursor()
        self.clear()
    def close(self):
        """Sever link to :class:`~fdb.Connection`.
        
        :raises ProgrammingError: If Monitor object was set as internal (via 
            :meth:`_set_as_internal`).
        """
        if self.__internal:
            raise fdb.ProgrammingError("Call to 'close' not allowed for embedded Monitor.")
        self._close()
        self.clear()
    def clear(self):
        """Drop all cached information objects. Force reload of fresh monitoring
        information on next reference."""
        self.__database = None
        self.__attachments = None
        self.__transactions = None
        self.__statements = None
        self.__callstack = None
        self.__iostats = None
        self.__variables = None
        if not self.closed:
            self._ic.transaction.commit()
    def refresh(self):
        "Reloads fresh monitoring information."
        self.__fail_if_closed()
        self._ic.transaction.commit()
        self.clear()
        self._get_database()
    def get_attachment(self,id):
        """Get :class:`AttachmentInfo` by ID.

        :param int id: Attachment ID.
        
        :returns: :class:`AttachmentInfo` with specified ID or `None`.
        """
        for attachment in self.attachments:
            if attachment.id == id:
                return attachment
        else:
            return None
    def get_transaction(self,id):
        """Get :class:`TransactionInfo` by ID.

        :param int id: Transaction ID.
        
        :returns: :class:`TransactionInfo` with specified ID or `None`.
        """
        for transaction in self.transactions:
            if transaction.id == id:
                return transaction
        else:
            return None
    def get_statement(self,id):
        """Get :class:`StatementInfo` by ID.

        :param int id: Statement ID.
        
        :returns: :class:`StatementInfo` with specified ID or `None`.
        """
        for statement in self.statements:
            if statement.id == id:
                return statement
        else:
            return None
    def get_call(self,id):
        """Get :class:`CallStackInfo` by ID.

        :param int id: Callstack ID.
        
        :returns: :class:`CallStackInfo` with specified ID or `None`.
        """
        for call in self.callstack:
            if call.id == id:
                return call
        else:
            return None
        

class BaseInfoItem(object):
    "Base class for all database monitoring objects."
    #: Weak reference to parent :class:`Monitor` instance.
    monitor = None
    def __init__(self,monitor,attributes):
        self.monitor = monitor if type(monitor) == weakref.ProxyType else weakref.proxy(monitor)
        self._attributes = dict(attributes)

    #--- protected

    def _strip_attribute(self,attr):
        if self._attributes.get(attr):
            self._attributes[attr] = self._attributes[attr].strip()

    #--- Protected

    def _get_stat_id(self):
        return self._attributes.get('MON$STAT_ID')
    #--- properties

    stat_id = LateBindingProperty(_get_stat_id,None,None,"Internal ID.")

class DatabaseInfo(BaseInfoItem):
    "Information about attached database."
    def __init__(self,monitor,attributes):
        super(DatabaseInfo,self).__init__(monitor,attributes)

        self._strip_attribute('MON$DATABASE_NAME')
    
    #--- Protected

    def __get_name(self):
        return self._attributes['MON$DATABASE_NAME']
    def __get_page_size(self):
        return self._attributes['MON$PAGE_SIZE']
    def __get_ods(self):
        return float('%d.%d' % (self._attributes['MON$ODS_MAJOR'],
                                self._attributes['MON$ODS_MINOR']))
    def __get_oit(self):
        return self._attributes['MON$OLDEST_TRANSACTION']
    def __get_oat(self):
        return self._attributes['MON$OLDEST_ACTIVE']
    def __get_ost(self):
        return self._attributes['MON$OLDEST_SNAPSHOT']
    def __get_next_transaction(self):
        return self._attributes['MON$NEXT_TRANSACTION']
    def __get_cache_size(self):
        return self._attributes['MON$PAGE_BUFFERS']
    def __get_sql_dialect(self):
        return self._attributes['MON$SQL_DIALECT']
    def __get_shutdown_mode(self):
        return self._attributes['MON$SHUTDOWN_MODE']
    def __get_sweep_interval(self):
        return self._attributes['MON$SWEEP_INTERVAL']
    def __get_read_only(self):
        return bool(self._attributes['MON$READ_ONLY'])
    def __get_forced_writes(self):
        return bool(self._attributes['MON$FORCED_WRITES'])
    def __get_reserve_space(self):
        return bool(self._attributes['MON$RESERVE_SPACE'])
    def __get_created(self):
        return self._attributes['MON$CREATION_DATE']
    def __get_pages(self):
        return self._attributes['MON$PAGES']
    def __get_backup_state(self):
        return self._attributes['MON$BACKUP_STATE']
    def __get_iostats(self):
        for io in self.monitor.iostats:
            if (io.stat_id == self.stat_id) and (io.group == STAT_DATABASE):
                return io
        return None
    
    #--- properties

    name = property(__get_name,None,None,
        "Database pathname or alias.")
    page_size = property(__get_page_size,None,None,
        "Size of database page in bytes.")
    ods = property(__get_ods,None,None,
        "On-Disk Structure (ODS) version number.")
    oit = property(__get_oit,None,None,
        "Transaction ID of the oldest [interesting] transaction.")
    oat = property(__get_oat,None,None,
        "Transaction ID of the oldest active transaction.")
    ost = property(__get_ost,None,None,
        "Transaction ID of the Oldest Snapshot, i.e., the number of the OAT " \
        "when the last garbage collection was done.")
    next_transaction = property(__get_next_transaction,None,None,
        "Transaction ID of the next transaction that will be started.")
    cache_size = property(__get_cache_size,None,None,
        "Number of pages allocated in the page cache.")
    sql_dialect = property(__get_sql_dialect,None,None,
        "SQL dialect of the database.")
    shutdown_mode = property(__get_shutdown_mode,None,None,
        "Current shutdown mode.")
    sweep_interval = property(__get_sweep_interval,None,None,
        "The sweep interval configured in the database header. " \
        "Value 0 indicates that sweeping is disabled.")
    read_only = property(__get_read_only,None,None,
        "True if database is Read Only.")
    forced_writes = property(__get_forced_writes,None,None,
        "True if database uses synchronous writes.")
    reserve_space = property(__get_reserve_space,None,None,
        "True if database reserves space on data pages.")
    created = property(__get_created,None,None,
        "Creation date and time, i.e., when the database was created or last restored.")
    pages = property(__get_pages,None,None,
        "Number of pages allocated on disk.")
    backup_state = property(__get_backup_state,None,None,
        "Current state of database with respect to nbackup physical backup.")
    iostats = property(__get_iostats,None,None,
        ":class:`IOStatsInfo` for this object.")

class AttachmentInfo(BaseInfoItem):
    "Information about attachment (connection) to database."
    def __init__(self,monitor,attributes):
        super(AttachmentInfo,self).__init__(monitor,attributes)

        self._strip_attribute('MON$ATTACHMENT_NAME')
        self._strip_attribute('MON$USER')
        self._strip_attribute('MON$ROLE')
        self._strip_attribute('MON$REMOTE_PROTOCOL')
        self._strip_attribute('MON$REMOTE_ADDRESS')
        self._strip_attribute('MON$REMOTE_PROCESS')
    
    #--- Protected

    def __get_id(self):
        return self._attributes['MON$ATTACHMENT_ID']
    def __get_server_pid(self):
        return self._attributes['MON$SERVER_PID']
    def __get_state(self):
        return self._attributes['MON$STATE']
    def __get_name(self):
        return self._attributes['MON$ATTACHMENT_NAME']
    def __get_user(self):
        return self._attributes['MON$USER']
    def __get_role(self):
        return self._attributes['MON$ROLE']
    def __get_remote_protocol(self):
        return self._attributes['MON$REMOTE_PROTOCOL']
    def __get_remote_address(self):
        return self._attributes['MON$REMOTE_ADDRESS']
    def __get_remote_pid(self):
        return self._attributes['MON$REMOTE_PID']
    def __get_remote_process(self):
        return self._attributes['MON$REMOTE_PROCESS']
    def __get_character_set(self):
        return self.monitor._con.schema.get_character_set_by_id(self._attributes['MON$CHARACTER_SET_ID'])
    def __get_timestamp(self):
        return self._attributes['MON$TIMESTAMP']
    def _get_transactions(self):
        return [t for t in self.monitor.transactions
                if t._attributes['MON$ATTACHMENT_ID'] == self.id]
    def _get_statements(self):
        return [s for s in self.monitor.statements
                if s._attributes['MON$ATTACHMENT_ID'] == self.id]
    def _get_variables(self):
        return [s for s in self.monitor.variables
                if s._attributes['MON$ATTACHMENT_ID'] == self.id]
    def __get_iostats(self):
        for io in self.monitor.iostats:
            if (io.stat_id == self.stat_id) and (io.group == STAT_ATTACHMENT):
                return io
        return None
    
    #--- properties

    id = property(__get_id,None,None,
        "Attachment ID.")
    server_pid = property(__get_server_pid,None,None,
        "Server process ID.")
    state = property(__get_state,None,None,
        "Attachment state (idle/active).")
    name = property(__get_name,None,None,
        "Database pathname or alias.")
    user = property(__get_user,None,None,
        "User name.")
    role = property(__get_role,None,None,
        "Role name.")
    remote_protocol = property(__get_remote_protocol,None,None,
        "Remote protocol name.")
    remote_address = property(__get_remote_address,None,None,
        "Remote address.")
    remote_pid = property(__get_remote_pid,None,None,
        "Remote client process ID.")
    remote_process = property(__get_remote_process,None,None,
        "Remote client process pathname.")
    character_set = property(__get_character_set,None,None,
        ":class:`~fdb.schema.CharacterSet` for this attachment.")
    timestamp = property(__get_timestamp,None,None,
        "Attachment date/time.")
    transactions = LateBindingProperty(_get_transactions,None,None,
        "List of transactions associated with attachment.\nItems are :class:`TransactionInfo` objects.")
    statements = LateBindingProperty(_get_statements,None,None,
        "List of statements associated with attachment.\nItems are :class:`StatementInfo` objects.")
    variables = LateBindingProperty(_get_variables,None,None,
        "List of variables associated with attachment.\nItems are :class:`ContextVariableInfo` objects.")
    iostats = property(__get_iostats,None,None,
        ":class:`IOStatsInfo` for this object.")

    #--- Public

    def isactive(self):
        "Returns True if attachment is active."
        return self.state == STATE_ACTIVE
    def isidle(self):
        "Returns True if attachment is idle."
        return self.state == STATE_IDLE
    def isgcallowed(self):
        "Returns True if Garbage Collection is enabled for this attachment."
        return bool(self._attributes['MON$GARBAGE_COLLECTION'])
    def terminate(self):
        """Terminates client session associated with this attachment.
        
        :raises ProgrammingError: If database has ODS lower than 11.2 or
            this attachement is current session.
        """
        if self.monitor._con.ods < fdb.ODS_FB_25:
            raise fdb.ProgrammingError("Attachments could be terminated only " \
                                       "for databases with ODS 11.2 and higher.")
        elif self is self.monitor.this_attachment:
            raise fdb.ProgrammingError("Can't terminate current session.")
        else:
            self.monitor._ic.execute('delete from mon$attachments where mon$attachment_id = ?',
                                     (self.id,))


class TransactionInfo(BaseInfoItem):
    "Information about transaction."
    def __init__(self,monitor,attributes):
        super(TransactionInfo,self).__init__(monitor,attributes)
    
    #--- Protected

    def __get_id(self):
        return self._attributes['MON$TRANSACTION_ID']
    def __get_attachment(self):
        return self.monitor.get_attachment(self._attributes['MON$ATTACHMENT_ID'])
    def __get_state(self):
        return self._attributes['MON$STATE']
    def __get_timestamp(self):
        return self._attributes['MON$TIMESTAMP']
    def __get_top(self):
        return self._attributes['MON$TOP_TRANSACTION']
    def __get_oldest(self):
        return self._attributes['MON$OLDEST_TRANSACTION']
    def __get_oldest_active(self):
        return self._attributes['MON$OLDEST_ACTIVE']
    def __get_isolation_mode(self):
        return self._attributes['MON$ISOLATION_MODE']
    def __get_lock_timeout(self):
        return self._attributes['MON$LOCK_TIMEOUT']
    def _get_statements(self):
        return [s for s in self.monitor.statements
                if s._attributes['MON$TRANSACTION_ID'] == self.id]
    def _get_variables(self):
        return [s for s in self.monitor.variables
                if s._attributes['MON$TRANSACTION_ID'] == self.id]
    def __get_iostats(self):
        for io in self.monitor.iostats:
            if (io.stat_id == self.stat_id) and (io.group == STAT_TRANSACTION):
                return io
        return None
    
    #--- properties

    id = property(__get_id,None,None,
        "Transaction ID.")
    attachment = property(__get_attachment,None,None,
        ":class:`AttachmentInfo` instance to which this transaction belongs.")
    state = property(__get_state,None,None,
        "Transaction state (idle/active).")
    timestamp = property(__get_timestamp,None,None,
        "Transaction start date/time.")
    top = property(__get_top,None,None,
        "Top transaction.")
    oldest = property(__get_oldest,None,None,
        "Oldest transaction (local OIT).")
    oldest_active = property(__get_oldest_active,None,None,
        "Oldest active transaction (local OAT).")
    isolation_mode = property(__get_isolation_mode,None,None,
        "Transaction isolation mode code.")
    lock_timeout = property(__get_lock_timeout,None,None,
        "Lock timeout.")
    statements = LateBindingProperty(_get_statements,None,None,
        "List of statements associated with transaction.\nItems are :class:`StatementInfo` objects.")
    variables = LateBindingProperty(_get_variables,None,None,
        "List of variables associated with transaction.\nItems are :class:`ContextVariableInfo` objects.")
    iostats = property(__get_iostats,None,None,
        ":class:`IOStatsInfo` for this object.")

    #--- Public

    def isactive(self):
        "Returns True if transaction is active."
        return self.state == STATE_ACTIVE
    def isidle(self):
        "Returns True if transaction is idle."
        return self.state == STATE_IDLE
    def isreadonly(self):
        "Returns True if transaction is Read Only."
        return self._attributes['MON$READ_ONLY'] == FLAG_SET
        #return bool(self._attributes['MON$READ_ONLY'])
    def isautocommit(self):
        "Returns True for autocommited transaction."
        return self._attributes['MON$AUTO_COMMIT'] == FLAG_SET
        #return bool(self._attributes['MON$AUTO_COMMIT'])
    def isautoundo(self):
        "Returns True for transaction with automatic undo."
        return self._attributes['MON$AUTO_UNDO'] == FLAG_SET
        #return bool(self._attributes['MON$AUTO_UNDO'])

class StatementInfo(BaseInfoItem):
    "Information about executed SQL statement."
    def __init__(self,monitor,attributes):
        super(StatementInfo,self).__init__(monitor,attributes)

        self._strip_attribute('MON$SQL_TEXT')

    #--- Protected

    def __get_id(self):
        return self._attributes['MON$STATEMENT_ID']
    def __get_attachment(self):
        return self.monitor.get_attachment(self._attributes['MON$ATTACHMENT_ID'])
    def __get_transaction(self):
        tr = self._attributes['MON$TRANSACTION_ID']
        return None if tr is None else self.monitor.get_transaction(tr)
    def __get_state(self):
        return self._attributes['MON$STATE']
    def __get_timestamp(self):
        return self._attributes['MON$TIMESTAMP']
    def __get_sql_text(self):
        return self._attributes['MON$SQL_TEXT']
    def __get_callstack(self):
        callstack = [x for x in self.monitor.callstack 
                  if ((x._attributes['MON$STATEMENT_ID'] == self.id) and 
                      (x._attributes['MON$CALLER_ID'] is None))]
        if len(callstack) > 0:
            item = callstack[0]
            while item is not None:
                caller_id = item.id
                item = None
                for x in self.monitor.callstack:
                    if x._attributes['MON$CALLER_ID'] == caller_id:
                        callstack.append(x)
                        item = x
                        break
        return callstack
    def __get_iostats(self):
        for io in self.monitor.iostats:
            if (io.stat_id == self.stat_id) and (io.group == STAT_STATEMENT):
                return io
        return None
    
    #--- properties

    id = property(__get_id,None,None,
        "Statement ID.")
    attachment = property(__get_attachment,None,None,
        ":class:`AttachmentInfo` instance to which this statement belongs.")
    transaction = property(__get_transaction,None,None,
        ":class:`TransactionInfo` instance to which this statement belongs or None.")
    state = property(__get_state,None,None,
        "Statement state (idle/active).")
    timestamp = property(__get_timestamp,None,None,
        "Statement start date/time.")
    sql_text = property(__get_sql_text,None,None,
        "Statement text, if appropriate.")
    callstack = property(__get_callstack,None,None,
        "List with call stack for statement.\nItems are :class:`CallStackInfo` objects.")
    iostats = property(__get_iostats,None,None,
        ":class:`IOStatsInfo` for this object.")

    #--- Public

    def isactive(self):
        "Returns True if statement is active."
        return self.state == STATE_ACTIVE
    def isidle(self):
        "Returns True if statement is idle."
        return self.state == STATE_IDLE
    def terminate(self):
        """Terminates execution of statement.

        :raises ProgrammingError: If this attachement is current session.
        """
        if self.attachment == self.monitor.this_attachment:
            raise fdb.ProgrammingError("Can't terminate statement from current session.")
        else:
            self.monitor._ic.execute('delete from mon$statements where mon$statement_id = ?',
                                     (self.id,))

class CallStackInfo(BaseInfoItem):
    "Information about PSQL call (stack frame)."
    def __init__(self,monitor,attributes):
        super(CallStackInfo,self).__init__(monitor,attributes)

        self._strip_attribute('MON$OBJECT_NAME')

    #--- Protected

    def __get_id(self):
        return self._attributes['MON$CALL_ID']
    def __get_statement(self):
        return self.monitor.get_statement(self._attributes['MON$STATEMENT_ID'])
    def __get_caller(self):
        return self.monitor.get_call(self._attributes['MON$CALLER_ID'])
    def __get_dbobject(self):
        obj_name = self._attributes['MON$OBJECT_NAME']
        obj_type = self._attributes['MON$OBJECT_TYPE']
        if obj_type == 5: # procedure
            return self.monitor._con.schema.get_procedure(obj_name)
        elif obj_type == 2: # trigger
            return self.monitor._con.schema.get_trigger(obj_name)
        else:
            raise fdb.ProgrammingError("Unrecognized object type '%d'" % obj_type)
    def __get_timestamp(self):
        return self._attributes['MON$TIMESTAMP']
    def __get_line(self):
        return self._attributes['MON$SOURCE_LINE']
    def __get_column(self):
        return self._attributes['MON$SOURCE_COLUMN']
    def __get_iostats(self):
        for io in self.monitor.iostats:
            if (io.stat_id == self.stat_id) and (io.group == STAT_CALL):
                return io
        return None

    #--- properties

    id = property(__get_id,None,None,
        "Call ID.")
    statement = property(__get_statement,None,None,
        "Top-level :class:`StatementInfo` instance to which this call stack entry belongs.")
    caller = property(__get_caller,None,None,
        "Call stack entry (:class:`CallStackInfo`) of the caller.")
    dbobject = property(__get_dbobject,None,None,
        "PSQL object. :class:`~fdb.schema.Procedure` or :class:`~fdb.schema.Trigger` instance.")
    timestamp = property(__get_timestamp,None,None,
        "Request start date/time.")
    line = property(__get_line,None,None,
        "SQL source line number.")
    column = property(__get_column,None,None,
        "SQL source column number.")
    iostats = property(__get_iostats,None,None,
        ":class:`IOStatsInfo` for this object.")

    #--- Public

class IOStatsInfo(BaseInfoItem):
    "Information about page and row level I/O operations, and about memory consumption."
    def __init__(self,monitor,attributes):
        super(IOStatsInfo,self).__init__(monitor,attributes)

    #--- Protected

    def __get_owner(self):
        def find(seq):
            for x in seq:
                if x.stat_id == self.stat_id:
                    return x
            return None
            
        obj_type = self.group
        if obj_type == STAT_DATABASE:
            return self.monitor.db
        elif obj_type == STAT_ATTACHMENT:
            return find(self.monitor.attachments)
        elif obj_type == STAT_TRANSACTION:
            return find(self.monitor.transactions)
        elif obj_type == STAT_STATEMENT:
            return find(self.monitor.statements)
        elif obj_type == STAT_CALL:
            return find(self.monitor.callstack)
        else:
            raise fdb.ProgrammingError("Unrecognized stat group '%d'" % obj_type)
    def __get_group(self):
        return self._attributes['MON$STAT_GROUP']
    def __get_reads(self):
        return self._attributes['MON$PAGE_READS']
    def __get_writes(self):
        return self._attributes['MON$PAGE_WRITES']
    def __get_fetches(self):
        return self._attributes['MON$PAGE_FETCHES']
    def __get_marks(self):
        return self._attributes['MON$PAGE_MARKS']
    def __get_seq_reads(self):
        return self._attributes['MON$RECORD_SEQ_READS']
    def __get_idx_reads(self):
        return self._attributes['MON$RECORD_IDX_READS']
    def __get_inserts(self):
        return self._attributes['MON$RECORD_INSERTS']
    def __get_updates(self):
        return self._attributes['MON$RECORD_UPDATES']
    def __get_deletes(self):
        return self._attributes['MON$RECORD_DELETES']
    def __get_backouts(self):
        return self._attributes['MON$RECORD_BACKOUTS']
    def __get_purges(self):
        return self._attributes['MON$RECORD_PURGES']
    def __get_expunges(self):
        return self._attributes['MON$RECORD_EXPUNGES']
    def __get_memory_used(self):
        return self._attributes.get('MON$MEMORY_USED')
    def __get_memory_allocated(self):
        return self._attributes.get('MON$MEMORY_ALLOCATED')
    def __get_max_memory_used(self):
        return self._attributes.get('MON$MAX_MEMORY_USED')
    def __get_max_memory_allocated(self):
        return self._attributes.get('MON$MAX_MEMORY_ALLOCATED')

    #--- properties

    owner = property(__get_owner,None,None,
        """Object that owns this IOStats instance. Could be either 
        :class:`DatabaseInfo`, :class:`AttachmentInfo`, :class:`TransactionInfo`, 
        :class:`StatementInfo` or :class:`CallStackInfo` instance.""")
    group = property(__get_group,None,None,
        "Object group code.")
    reads = property(__get_reads,None,None,
        "Number of page reads.")
    writes = property(__get_writes,None,None,
        "Number of page writes.")
    fetches = property(__get_fetches,None,None,
        "Number of page fetches.")
    marks = property(__get_marks,None,None,
        "Number of pages with changes pending.")
    seq_reads = property(__get_seq_reads,None,None,
        "Number of records read sequentially.")
    idx_reads = property(__get_idx_reads,None,None,
        "Number of records read via an index.")
    inserts = property(__get_inserts,None,None,
        "Number of inserted records.")
    updates = property(__get_updates,None,None,
        "Number of updated records.")
    deletes = property(__get_deletes,None,None,
        "Number of deleted records.")
    backouts = property(__get_backouts,None,None,
        "Number of records where a new primary record version or a change to " \
        "an existing primary record version is backed out due to rollback or " \
        "savepoint undo.")
    purges = property(__get_purges,None,None,
        "Number of records where record version chain is being purged of " \
        "versions no longer needed by OAT or younger transactions.")
    expunges = property(__get_expunges,None,None,
        "Number of records where record version chain is being deleted due to " \
        "deletions by transactions older than OAT.")
    memory_used = property(__get_memory_used,None,None,
        "Number of bytes currently in use.")
    memory_allocated = property(__get_memory_allocated,None,None,
        "Number of bytes currently allocated at the OS level.")
    max_memory_used = property(__get_max_memory_used,None,None,
        "Maximum number of bytes used by this object.")
    max_memory_allocated = property(__get_max_memory_allocated,None,None,
        "Maximum number of bytes allocated from the operating system by this object.")

    #--- Public

class ContextVariableInfo(BaseInfoItem):
    "Information about context variable."
    def __init__(self,monitor,attributes):
        super(ContextVariableInfo,self).__init__(monitor,attributes)

        self._strip_attribute('MON$VARIABLE_NAME')
        self._strip_attribute('MON$VARIABLE_VALUE')

    #--- Protected

    def __get_attachment(self):
        return self.monitor.get_attachment(self._attributes['MON$ATTACHMENT_ID'])
    def __get_transaction(self):
        tr = self._attributes['MON$TRANSACTION_ID']
        return None if tr is None else self.monitor.get_transaction(tr)
    def __get_name(self):
        return self._attributes['MON$VARIABLE_NAME']
    def __get_value(self):
        return self._attributes['MON$VARIABLE_VALUE']

    #--- properties

    attachment = property(__get_attachment,None,None,
        ":class:`AttachmentInfo` instance to which this context variable belongs or None.")
    transaction = property(__get_transaction,None,None,
        ":class:`TransactionInfo` instance to which this context variable belongs or None.")
    name = property(__get_name,None,None,"Context variable name.")
    value = property(__get_value,None,None,"Value of context variable.")

    #--- Public

    def isattachmentvar(self):
        "Returns True if variable is associated to attachment context."
        return self._attributes['MON$ATTACHMENT_ID'] is not None
    def istransactionvar(self):
        "Returns True if variable is associated to transaction context."
        return self._attributes['MON$TRANSACTION_ID'] is not None
    