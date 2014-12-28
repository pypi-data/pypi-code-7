from sqlalchemy import Column
from sqlalchemy import FetchedValue
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import DateTime

from fulcrum.const import SCHEMA_ENTITIES
from fulcrum.orm.base import EntityRelation


TABLE_NAME = 'principals'
DOCSTRING = """Maps the ``{0}.{1}`` relation to a Python object."""\
    .format(SCHEMA_ENTITIES, TABLE_NAME)


class Principal(EntityRelation):
    __doc__ = DOCSTRING
    __tablename__ = TABLE_NAME
    __table_args__ = {
        'schema': SCHEMA_ENTITIES
    }

    principal_id = Column(BigInteger,
        server_default=FetchedValue(),
        primary_key=True,
        name='principal_id'
    )

    subtype = Column(String,
        nullable=False,
        name='subtype'
    )

    date_registered = Column(DateTime(timezone=True),
        nullable=False,
        name='date_registered'
    )
