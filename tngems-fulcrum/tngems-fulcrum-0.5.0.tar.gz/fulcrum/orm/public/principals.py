from sqlalchemy import Column
from sqlalchemy import FetchedValue
from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Boolean

from fulcrum.const import SCHEMA_PUBLIC
from fulcrum.orm.base import PublicRelation


class Principal(PublicRelation):
    """Maps the ``public.principals`` table to a Python object."""
    __tablename__ = 'principals'
    __table_args__ = {
        'schema': SCHEMA_PUBLIC
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

    is_active = Column(Boolean,
        nullable=False,
        default=False,
        name='is_active'
    )

    username = Column(String,
        nullable=False,
        default='',
        name='username'
    )

    email_address = Column(String,
        nullable=False,
        default='',
        name='email_address'
    )
