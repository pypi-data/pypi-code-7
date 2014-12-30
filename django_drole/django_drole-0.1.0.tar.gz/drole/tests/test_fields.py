from drole.fields import RoleField, PermissionField
from drole.types import Role, Permission

class BaseFieldTest(object):
    field = None
    type = None

    def test_none_to_python(self):
        f = self.field()
        assert f.to_python(None) is None

    def test_string_to_python(self):
        f = self.field()
        assert f.to_python('x') == self.type('x')

    def test_type_to_python(self):
        f = self.field()
        assert f.to_python(self.type('x')) == self.type('x')

    def test_string_to_db(self):
        f = self.field()
        assert f.get_prep_value('string') == 'string'

class TestRoleField(BaseFieldTest):
    field = RoleField
    type = Role

class TestPermissionField(BaseFieldTest):
    field = PermissionField
    type = Permission

