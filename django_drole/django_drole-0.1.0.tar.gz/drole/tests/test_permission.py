import pytest
from drole.types import Permission, Role

@pytest.fixture
def clean_registry():
    Permission._registry.clear()

@pytest.mark.usefixtures("clean_registry")    
class TestPermission(object):
    """
        Permission is a simple wrapper around a string identifier
        with some singleton-ish behaviour
    """
    def test_unicode(self):
        assert isinstance(Permission.create("foo").__unicode__(), unicode)

    def test_create(self):
        """ Permissions are implicitly created """
        assert Permission.create("foo") is not None

    def test_uniqueness_id(self):
        """ Different instances with same identifier are identical """
        assert Permission.create("foo") is Permission.create("foo")

    def test_uniqueness_attrs(self):
        """ Different instances with same identifier are identical, even
            if other attributes differ """
        assert Permission.create("foo", "bar", "bla") is \
               Permission.create("foo", "this", "that")

    def test_uniqueness_differ(self):
        """ 
            Permissions with different identifier are not equal
        """
        assert Permission.create("foo") != Permission.create("bar")

    def test_equality(self):
        """ ordinary comparison. Will succeed since it will be the same
            objects """
        assert Permission.create("foo") == Permission.create("foo")

    def test_forced_equality(self):
        """ if somehow different permissions get created with the same
            identifier, they should still be equal """
        assert Permission("foo") == Permission("foo")

    def test_forced_inequality(self):
        """ if somehow different permissions get created with different
            identifiers, they shouldn't be equal """
        assert Permission("foo") != Permission("bar")

    def test_forced_identity(self):
        """ if somehow different permissions get created with the same
            identifier, they are equal but not identical """
        assert Permission("foo") is not Permission("foo")

    def test_in(self):
        """ a common case """
        assert Permission("foo") in [Permission("bar"),
                                     Permission("foo"), Permission("hello")]

    def test_all_empty(self):
        """ empty role collection """
        assert len(Permission.all()) == 0

    def test_all(self):
        """ retrieve all created permissions """
        p1 = Permission.create("r1")
        p2 = Permission.create("r2")
        p3 = Permission.create("r2") # duplicate!
        assert set(Permission.all()) == set((p1, p2))

    def test_hash(self):
        """ verify permissions can be hashed properly """
        assert set((Permission("r1"),)) == set((Permission("r1"),))

    def test_hash_perm_role(self):
        """ Permission / Role are hashed differently, even with same id """
        assert set((Permission("r1"),)) != set((Role("r1"),))
