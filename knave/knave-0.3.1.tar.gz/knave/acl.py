# Copyright 2014 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""\
An ACL is a mapping of users to permissions via roles.

The base ACL object requires two mappings:

1. Permissions to roles (what roles are authorized for permission X?)
2. User to roles (what roles is user Y a member of?)

Using these two mappings, the ACL is able to determine whether authorization
should be granted or not.
"""
from collections import defaultdict
from . import roles, identity, predicates

__all__ = ['ACL', 'Role', 'Permission']


class ACL(roles.RoleProvider):

    environ_key = 'knave.acl'
    environ = None

    def __init__(self, role_providers, permissions_map,
                 identity_adapter=identity.RemoteUserIdentityAdapter()):

        self._source_role_providers = []
        self._permission_roles = defaultdict(set)

        self.identity_adapter = identity_adapter
        self.add_role_providers(role_providers)

        for p, roles in permissions_map.items():
            self._permission_roles[p] |= roles

    def test(self, predicate, context=None, identity=None):
        """
        Test a predicate, returning a boolean result
        """
        if identity is None:
            identity = self.identity_adapter(self.environ)
        return predicate(self, identity, context)

    def require(self, predicate, context=None, identity=None,
                exc=predicates.Unauthorized):
        """
        Test a predicate, and raise Unauthorized if it is not met
        """
        if identity is None:
            identity = self.identity_adapter(self.environ)
        if not predicate(self, identity, context):
            raise exc()
        return True

    def bind_to(self, environ):
        """
        Return a new ACL bound to WSGI environ dict ``environ``
        """
        bound_acl = ACL.__new__(ACL)
        bound_acl.__dict__ = self.__dict__.copy()
        bound_acl.environ = environ
        bound_acl._role_provider = \
                roles.CachingRoleProvider(self._role_provider, {})
        environ[self.environ_key] = bound_acl
        return bound_acl

    @classmethod
    def of(cls, environ):
        return environ[cls.environ_key]

    def get_identity(self):
        return self.identity_adapter(self.environ)

    def add_role_providers(self, role_providers):
        self._source_role_providers.extend(role_providers)
        self._role_provider = \
                make_role_provider(self._source_role_providers)

    def role_provider(self, provider_or_role, contextual=False):
        """
        Add a RoleProvider to the ACL

        `provider_or_role` may be either an instance of
        `class:~knave.roles.RoleProvider`, in which case the provider will be
        added directly, or a Role, in which case a function decorator will be
        returned that adds the decorated function using
        `func:~knave.roles.role_decider`.
        """
        if isinstance(provider_or_role, type) and \
                issubclass(provider_or_role, roles.RoleProvider):
            self.add_role_providers([provider_or_role()])
        elif isinstance(provider_or_role, roles.RoleProvider):
            self.add_role_providers([provider_or_role])
        else:
            def role_provider_decorator(fn):
                provider = roles.role_decider(provider_or_role, contextual)(fn)
                self.add_role_providers([provider])
            return role_provider_decorator

    def roles_for_permission(self, permission):
        """\
        Return the roles required to satisfy ``permission``.
        """
        return self._permission_roles[permission]

    def any_matching(self, roles, identity, context=None):
        """
        Implement the role provider interface
        """
        return self._role_provider.any_matching(roles, identity, context)

    def member_subset(self, roles, identity, context=None):
        """
        Implement the role provider interface
        """
        return self._role_provider.member_subset(roles, identity, context)

    def has_permission(self, permission, context=None, identity=None):
        """\
        Return `True` if the identified user has the given permission in
        ``context``
        """
        if identity is None:
            identity = self.get_identity()
        return permission(self, identity, context)

    def has_role(self, role, context=None, identity=None):
        """\
        Return `True` if the identified user has the given role in ``context``
        """
        if identity is None:
            identity = self.get_identity()
        return self._role_provider.has_any({role}, identity, context)

    def is_authenticated(self):
        return self.identity_adapter.is_authenticated(self.environ)


@predicates.make_predicate
def is_authenticated(acl, identity, context):
    """\
    The ``is_authenticated`` predicate returns True if a user is
    authenticated, regardless of whether they have any permissions
    assigned.
    """
    return acl.identity_adapter.is_authenticated(acl.environ)


class Permission(predicates.Predicate):
    """\
    A permission predicate checks the user's access rights against a
    list of roles that satisfy the permission.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Permission %r>' % (self.name,)

    def __call__(self, acl, identity, context=None):
        return acl.has_any(acl.roles_for_permission(self), identity, context)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Role(predicates.Predicate):
    """\
    A role predicate checks the user is assigned the given role
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % (self.name,)

    def __call__(self, acl, identity, context):
        return acl.has_role(self, identity, context)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def make_role_provider(role_providers):
    """
    Wrap multiple role providers in MultiRoleProvider
    """

    if len(role_providers) == 1:
        role_provider = role_providers[0]
    else:
        role_provider = roles.MultiRoleProvider(*role_providers)

    return role_provider
