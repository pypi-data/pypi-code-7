from sqlalchemy import func


class StoredProcedure(object):
    """Wraps a call to a stored procedure in a Python function."""

    def __init__(self, nspname, procname, rtype=lambda x: x, scalar=False):
        self.nspname = nspname
        self.procname = procname
        self.rtype = rtype
        self.scalar = scalar

    def prepare(self, *args, **kwargs):
        f = getattr(getattr(func, self.nspname), self.procname)
        return f(*args, **kwargs)

    def __call__(self, session, *args, **kwargs):
        f = self.prepare(*args, **kwargs)
        result = session.execute(f)
        if self.rtype is None:
            retval = None
        elif self.scalar:
            retval = self.rtype(result.scalar())
        else:
            retval = map(self.rtype, result.fetchall())
        return retval
