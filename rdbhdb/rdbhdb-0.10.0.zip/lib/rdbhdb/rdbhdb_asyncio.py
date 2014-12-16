
"""
  Python 3.3 dependent features are in this module, so that py2 and py3.2- apps do not choke on them.
  The import for py2 will fail, on ImportError or SyntaxError, but importing module will function.

  If import succeeds (py3.3+), these symbols are added to importing module, so this module name is not used by
    client.
"""


from rdbhdb.rdbhdb import *

try:
    import asyncio
    #import aiohttp
    from yieldfrom import urllib3 as u3
except ImportError:
    pass

src = '''

class AsyncConnection(Connection):
    """Async Connection.
    works like rdbhdb.Connection, except provides async cursors
    """

    def __init__(self, host, role, authcode):
        """init"""
        Connection.__init__(self, host, role, authcode)

    def cursor(self, cursor_factory=None):
        """Create cursor.  If autorefill is set to true, will create
        an autorefilling cursor.  Otherwise not.  Passing a cursor class
        as the 'cursor_factory' will create that type of cursor.
        """
        #self._lock.acquire()
        try:
            if not cursor_factory:
                cur = AsyncCursor(self)
            else:
                cur = cursor_factory(self)
            if self.autorefill:
                cur = AsyncAutoRefill(self, cur)
        finally:
            #self._lock.release()
            pass
        return cur


class AsyncCursor(Cursor):
    """Async Cursor.
    works like rdbhdb.Cursor, except uses asyncio.
    """

    @asyncio.coroutine
    def execute(self, query, args=()):
        """Execute query with optional args """
        assert type(args) in (type((1, 2)), type([]), type({}), type(None)), (type(args), args)
        yield from self._execute(query, args, (), ())

    @asyncio.coroutine
    def executemany(self, query, argslist):
        """Execute query multiple times, once per arg set."""
        for a in argslist:
            yield from self._execute(query, a, (), ())
        self.rowcount = -1
        return None

    @asyncio.coroutine
    def execute_deferred(self, query, args=()):
        """Execute query with optional args, so that execution is deferred
        until after method returns.
        """
        addparms = (('deferred', 'yes'), )
        yield from self._execute(query, args, addparms, ())

    @asyncio.coroutine
    def _execute(self, query, args, otherparms, addhdrs):
        """Private method to handle core of execute and executemany """

        if not self.conn or not self.conn._authItems:
            raise ProgrammingError('-', 'Connection closed before execute')

        query, parms = self._prep_query_parms(query, args, otherparms)

        datareceived = stuff = False
        host, role, authcode = self.conn._authItems

        for _i in range(3):
            txt = ''
            try:
                _r = yield from self.get_data_from_server(role, authcode, host, 'json', query, parms, addhdrs)
                hdrs, txt = _r
                self._rawbodysize = len(txt)
                stuff = json.loads(txt)
                if stuff['status'][0] != 'error' or stuff['error'][0] != 'rdb03':  # if query timeout, retry
                    datareceived = True
                    break
                else:
                    time.sleep(0.25)
                    continue

            except ValueError as e:
                raise InterfaceError('??', 'JSON not converted [%s]' % txt)

            except u3.exceptions.ConnectTimeoutError as e:
                continue

            except u3.exceptions.HTTPError as e:
                break

        if not datareceived:
            raise InterfaceError('rdbhdb09', 'Http connection failed -> received %s' % txt)

        return self._process_results(stuff)

    @asyncio.coroutine
    def get_data_from_server(self, role, authcode, host, fmt, q, flds, addhdrs):
        """post fields to url via POST, return result page. """

        url, body, headers = self._prep_url_body_header(role, authcode, fmt, q, flds, addhdrs)

        conn = u3.HTTPSConnectionPool(host, timeout=20)
        r = yield from conn.urlopen('POST', url, body=body, headers=headers, retries=5, assert_same_host=True)


        # return headers and body
        headers = r.headers
        text = (yield from r.data).decode('utf-8')

        return headers, text


class AsyncAutoRefill(AutoRefill):

    @asyncio.coroutine
    def execute(self, query, args=()):

        self._args = args
        self._query = query
        yield from self._cursor.execute(query, args)

    @asyncio.coroutine
    def executemany(self, query, argslist):
        """Execute query multiple times, once per arg set."""

        for a in argslist:
            yield from self.execute(query, a)
        self._cursor.rowcount = -1
        return None

    @asyncio.coroutine
    def _refill_records(self):
        """Resubmit query to retrieve additional records beyond
        the previous truncation point using SQL's OFFSET modifier.
        """

        self._offset += 100
        query = modify_query(self._query, self._offset)
        rows = self._cursor._records
        self._cursor._records = []
        yield from self._cursor.execute(query, self._args)
        rows.extend(self._cursor._records)
        self._cursor._records = rows


'''
try:
    _c = compile(src, __name__, 'exec')
    exec(_c)
except SyntaxError as e:
    pass

