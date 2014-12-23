from sqlalchemy import Column
from sqlalchemy import FetchedValue
from sqlalchemy import BigInteger
from sqlalchemy import String

from fulcrum.const import SCHEMA_ENTITIES
from fulcrum.orm.base import EntityRelation


TABLE_NAME = 'inodes'
DOCSTRING = """Maps the ``{0}.{1}`` relation to a Python object."""\
    .format(SCHEMA_ENTITIES, TABLE_NAME)


class IndexNode(EntityRelation):
    __doc__ = DOCSTRING
    __tablename__ = TABLE_NAME
    __table_args__ = {
        'schema': SCHEMA_ENTITIES
    }

    inode_id = Column(BigInteger,
        server_default=FetchedValue(),
        primary_key=True,
        name='inode_id'
    )

    uuid4 = Column(String,
        server_default=FetchedValue(),
        unique=True,
        nullable=False,
        name='uuid4'
    )

    subtype = Column(String,
        nullable=False,
        name='subtype'
    )

    mimetype = Column(String,
        nullable=False,
        name='mimetype'
    )

    filename = Column(String,
        nullable=False,
        name='filename'
    )

