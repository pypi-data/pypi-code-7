from auditbwc.model.declarative import AuditRecordMixin
import savalidation.validators as val
import sqlalchemy.exc as saexc
from sqlalchemybwc.lib.declarative import declarative_base, DefaultMixin

Base = declarative_base()

try:
    class AuditRecord(Base, DefaultMixin, AuditRecordMixin):
        __tablename__ = 'tblAuditRecords'

        val.validates_constraints()
except saexc.InvalidRequestError, e:
    if 'already defined' not in str(e):
        raise
    pass
