from fulcrum.procedures.public import set_session_authorization


class Atomic(object):
    """Syntactic sugar for SQLAlchemy transaction management."""

    def __init__(self, session):
        self._session = session

    def in_transaction_block(self, session):
        """Return a tuple of booleans indicating if the current session is
        in a transaction block, and if the block is nested in an other block.
        """
        return (
            session.transaction is not None,
            getattr(session.transaction, '_parent', None) is not None
        )

    def commit(self):
        self.on_commit()
        self._session.commit()

    def rollback(self):
        self.on_rollback()
        self._session.rollback()

    def on_begin(self):
        """Hook that is executed right after the opening ``BEGIN`` (or
        ``SAVEPOINT``) statement.
        """
        pass

    def on_commit(self):
        """Hook that is executed right before a closing ``COMMIT`` (or
        ``RELEASE SAVEPOINT`` statement.
        """
        pass

    def on_rollback(self):
        """Hook that is executed right before a closing ROLLBACK
        statement.
        """
        pass

    def __enter__(self):
        session = self._session
        in_transaction, is_nested = self.in_transaction_block(session)
        self.transaction = session.begin(nested=in_transaction)
        self.on_begin()

    def __exit__(self, cls, exception, traceback):
        session = self._session
        if cls is None:
            try:
                self.commit()
                return
            except Exception:
                self.rollback()
                raise
        else:
            self.rollback()


class AuthorizedTransaction(Atomic):

    def __init__(self, session, user, client):
        self._user = user
        self._client = client
        Atomic.__init__(self, session)

    def on_begin(self):
        set_session_authorization(self._session, self._user, self._client)
