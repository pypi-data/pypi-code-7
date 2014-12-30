from libtng.hashers import make_password
from libsovereign.const import PASSWORD_HASHER

from fulcrum.loaders.entity import EntityLoader
from fulcrum.orm.public import Principal
from fulcrum.orm.public import Credentials


class PrincipalLoader(EntityLoader):
    entity_type = "auth.principal"
    dao_class   = Principal

    def clean_raw_password(self, item, value):
        item['passphrase'] = make_password(value, hasher=PASSWORD_HASHER)

    def init_dao(self, item):
        return self.dao_class(
            subtype = item.pop('subtype'),
            date_registered = item.pop('date_registered'),
            principal_id = item.pop('user_id', None)\
                or item.pop('principal_id', None),
            username = item.pop('username', None),
            email_address = item.pop('email_address', None),
            is_active = item.pop('is_active', False)
        )

    def persist_passphrase(self, item, dao, value):
        obj = Credentials(principal_id=dao.principal_id,
            passphrase=value)
        self._session.merge(obj)
