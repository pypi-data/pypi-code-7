from zope.sqlalchemy import datamanager
datamanager.NO_SAVEPOINT_SUPPORT = set()

from sqlalchemy import create_engine, event
from model_meta import DBSession, metadata, DeclarativeBase, User
from tgext.tagging.model.setup import setup_model

engine = create_engine('sqlite:///:memory:', echo=True)

@event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # Disable SQLITE automatic transactions
    dbapi_connection.isolation_level = None

@event.listens_for(engine, "begin")
def do_begin(conn):
    # Manually emit SQLITE transaction begin
    conn.execute("BEGIN")


setup_model(dict(
    DeclarativeBase=DeclarativeBase,
    metadata=metadata,
    DBSession=DBSession,
    User=User)
)


def setup():
    print('SETTING UP MODEL')
    DBSession.configure(bind=engine)
    metadata.create_all(engine)


def teardown():
    print('TEARING DOWN MODEL')
    metadata.drop_all(engine)

