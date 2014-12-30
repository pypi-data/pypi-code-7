import pytest
from drole.types import Role

@pytest.fixture
def clean_registry():
    Role._registry.clear()

@pytest.mark.usefixtures("clean_registry")    
class TestRole(object):
    """
        Role is a simple wrapper around a string identifier
        with some singleton-ish behaviour
    """
    def test_unicode(self):
        assert isinstance(Role.create("foo").__unicode__(), unicode)

    def test_create(self):
        """ Role are implicitly created """
        assert Role.create("foo") is not None

    def test_uniqueness_id(self):
        """ Different instances with same identifier are identical """
        assert Role.create("foo") is Role.create("foo")

    def test_uniqueness_attrs(self):
        """ Different instances with same identifier are identical, even
            if other attributes differ """
        assert Role.create("foo", "bar", "bla") is \
               Role.create("foo", "this", "that")

    def test_uniqueness_differ(self):
        """ 
            Role with different identifier are not equal
        """
        assert Role.create("foo") != Role("bar")

    def test_equality(self):
        """ ordinary comparison. Will succeed since it will be the same
            objects """
        assert Role.create("foo") == Role.create("foo")

    def test_forced_equality(self):
        """ if somehow different roles get created with the same identifier,
            they should still be equal """
        assert Role("foo") == Role("foo")

    def test_forced_inequality(self):
        """ if somehow different roles get created with different identifiers,
            they should not be equal """
        assert Role("foo") != Role("bar")

    def test_forced_identity(self):
        """ if somehow different roles get created with the same identifier,
            they are equal but not identical """
        assert Role("foo") is not Role("foo")

    def test_in(self):
        """ a common case """
        assert Role("foo") in [Role("bar"), Role("foo"), Role("hello")]

    def test_all_empty(self):
        """ empty role collection """
        assert len(Role.all()) == 0

    def test_all(self):
        """ retrieve all created permissions """
        r1 = Role.create("r1")
        r2 = Role.create("r2")
        r3 = Role.create("r2") # duplicate!
        assert set(Role.all()) == set((r1, r2))

    def test_hash(self):
        """ verify roles can be hashed properly """
        assert set((Role("r1"),)) == set((Role("r1"),))

