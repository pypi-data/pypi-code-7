import base64
from blazeutils.helpers import tolist
from blazeutils.strings import randchars
import sqlalchemy as sa
from sqlalchemybwc import db
from sqlalchemybwc.lib.decorators import transaction
import zlib


class AuditRecordMixin(object):

    identifier = sa.Column(sa.Unicode(50), nullable=False)
    audit_text = sa.Column(sa.Unicode(4000), nullable=False)
    comments = sa.Column(sa.Unicode(256))

    def get_previous_record(self):
        from compstack.audit.model.entities import AuditRecord
        return db.sess.query(AuditRecord).filter(
            AuditRecord.identifier == self.identifier,
            AuditRecord.createdts <= self.createdts,
            AuditRecord.id < self.id
        ).order_by(
            AuditRecord.createdts.desc(),
            AuditRecord.id.desc()
        ).first()

    @classmethod
    def get_latest_record(cls, identifier):
        from compstack.audit.model.entities import AuditRecord
        return db.sess.query(AuditRecord).filter(
            AuditRecord.identifier == identifier,
        ).order_by(
            AuditRecord.createdts.desc(),
            AuditRecord.id.desc()
        ).first()

    @classmethod
    def testing_create(cls, **kwargs):
        kwargs['identifier'] = kwargs.get('identifier', randchars(15))
        kwargs['audit_text'] = kwargs.get('audit_text', randchars(10))
        return cls.add(**kwargs)

    @classmethod
    def add_in_trans(cls, **kwargs):
        # audit text will be assigned as a plain string,
        #   but compress for storage
        if 'audit_text' in kwargs:
            bin_str = unicode(kwargs['audit_text']).encode('utf-8')
            kwargs['audit_text'] = unicode(
                base64.b64encode(zlib.compress(bin_str, 9))
            )
        o = cls()
        o.from_dict(kwargs)
        cls._sa_sess().add(o)
        return o

    @transaction
    def add(cls, **kwargs):
        return cls.add_in_trans(**kwargs)

    @property
    def full_text(self):
        return zlib.decompress(base64.b64decode(self.audit_text)).decode('utf-8')


class AuditTagMixin(object):
    @classmethod
    def _create_audit(cls, obj, **kwargs):
        """
            Creates a unique audit record for this revision. Pays attention
            to values in the entity's audit_meta property
        """
        from compstack.audit.model.entities import AuditRecord

        # filter args passed in to get the specific fields specified in meta
        field_dict = {
            k: kwargs.get(k) for k in tolist(cls.audit_meta.get('fields') or [])
        }

        # compute new audit text once, as it will be used a couple of times
        full_audit_text = obj.audit_text

        # check to see if there's any actual change, set flag accordingly
        previous_record = AuditRecord.get_latest_record(obj.audit_identifier)
        if previous_record and previous_record.full_text == full_audit_text:
            obj._audit_change = False
            return
        obj._audit_change = True

        # change detected, create an audit record
        AuditRecord.add_in_trans(
            identifier=obj.audit_identifier,
            audit_text=full_audit_text,
            comments=kwargs.get('audit_comments'),
            **field_dict
        )

    @transaction
    def add(cls, **kwargs):
        # standard add method, with call to generate audit record
        o = cls()
        o.from_dict(kwargs)
        cls._sa_sess().add(o)
        cls._sa_sess().flush()
        cls._create_audit(o, **kwargs)
        return o

    @transaction
    def edit(cls, oid=None, **kwargs):
        # standard edit method, with call to generate audit record
        try:
            oid = oid or kwargs.pop('id')
        except KeyError:
            raise ValueError('the id must be given to edit the record')
        o = cls.get(oid)
        o.from_dict(kwargs)
        cls._create_audit(o, **kwargs)
        return o

    @property
    def audit_meta(self):
        """
            Meta dict, optionally has a "tag" for identifying kinds of audit
            records. Also may have a "fields" list, to specify non-standard
            fields that could get set on the record entity, which may be
            passed into the entity's add or edit method
        """
        raise NotImplementedError('audit_meta must be defined on the entity')

    @property
    def audit_text(self):
        """
            Text representation of the auditable object. Full repr is stored
            for each point in time, so that diffs can be performed on any
            two revisions
        """
        raise NotImplementedError('audit_text must be defined on the entity')

    @property
    def audit_identifier(self):
        return u'{0}-{1}'.format(self.audit_meta.get('tag'), self.id)

    def check_audit_change(self):
        return getattr(self, '_audit_change', False)
