from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey

from fulcrum.const import SCHEMA_PUBLIC
from fulcrum.orm.base import PublicRelation
from fulcrum.orm.public.principals import Principal


class Credentials(PublicRelation):
    """Maps the ``public.credentials`` table to a Python object."""
    __tablename__ = 'credentials'
    __table_args__ = {
        'schema': SCHEMA_PUBLIC
    }

    principal_id = Column(ForeignKey(Principal.principal_id),
        primary_key=True,
        name='principal_id'
    )

    passphrase = Column(String,
        nullable=False,
        name='passphrase'
    )

