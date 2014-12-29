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

__all__ = ['RoleProvider', 'StaticRoleProvider']


class RoleProvider(object):

    #: If True, the RoleProvider will only called when a context is provided
    contextual = False

    #: Set of roles this RoleProvider can determine
    #: If empty the RoleProvider will be called for any query,
    #: otherwise it will only be called for queries concerning at least one of
    #: the indicated roles.
    determines = frozenset()

    def has_all(self, roles, identity, context=None):
        """\
        Return True if the identified user has all roles assigned in the given
        context.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :rtype: bool
        """
        if not roles:
            raise ValueError("Expected at least one role")
        return len(self.member_subset(roles, identity, context)) == len(roles)

    def has_any(self, roles, identity, context=None):
        """\
        Return true if the identified user is a member of any of the specified
        roles.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :rtype: bool
        """
        if not roles:
            raise ValueError("Expected at least one role")
        return bool(self.any_matching(roles, identity, context))

    def any_matching(self, roles, identity, context=None):
        """
        Return a subset of any items in ``roles`` of which the user is a
        member.

        This method is not required to return the complete subset of member
        roles - subclasses are free to override this with an implementation
        that it stops as soon as it finds the first role membership.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :returns: a subset of ``roles`` of which the current user is a member
        :rtype: :class:`set`
        """
        return self.member_subset(roles, identity, context=None)

    def member_subset(self, roles, identity, context=None):
        """
        Return the subset of ``roles`` to which the currently identified user
        is assigned.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :param context: Any context object (optional)
        :return: The subset of roles of which the current user has membership
        :rtype: :class:`set`
        """
        raise NotImplementedError


class CachingRoleProvider(RoleProvider):
    """\
    A role provider that wraps another and caches the results of lookups for
    the duration of the request
    """

    def __init__(self, provider, cache):
        self.provider = provider
        self.cache = cache

    def cached_roles(self, identity, context=None,):
        """\
        Return two sets of roles:
        - The set of roles which the current user is known to be in
        - The set of roles which the current user is known NOT to be in
        """
        return self.cache.setdefault((identity, context), (set(), set()))

    def member_subset(self, roles, identity, context=None):
        return self._member_subset(self.provider.member_subset, roles,
                                   identity, context)

    def any_matching(self, roles, identity, context=None, environ=None):
        return self._member_subset(self.provider.any_matching, roles,
                                   identity, context)

    def _member_subset(self, provider_lookup, roles, identity, context=None):

        cached_is_in, cached_not_in = self.cached_roles(identity, context)

        # Remove those roles we know immediately do not apply
        roles = roles - cached_not_in

        # Can we answer the query from the cache?
        if roles.issubset(cached_is_in):
            return roles

        # The cache doesn't contain enough information to answer the query. Ask
        # the downstream provider to fill in the gaps
        not_cached = roles - cached_is_in

        member_roles = provider_lookup(not_cached, identity, context)

        # Cache the roles to which the environ is known to belong or not,
        cached_is_in |= member_roles

        if provider_lookup is self.provider.member_subset:
            # member_subset can be relied on to return all roles for a member,
            # so we can safely infer negative roles
            cached_not_in |= not_cached - member_roles
        else:
            # with ``any_matching`` we can only infer negative membership in
            # the case that no roles matched (any_matching stops after the
            # first hit, so we do not know if the user may have other roles
            # that were not tested)
            if len(member_roles) == 0:
                cached_not_in |= not_cached

        return roles & cached_is_in


class MultiRoleProvider(RoleProvider):
    """\
    Role adapter that can handles multiple role providers.
    """

    def __init__(self, *providers):
        self.providers = list(providers)

    def any_matching(self, roles, identity, context=None):
        return self.member_subset(roles, identity, context, stop_on_match=True)

    def member_subset(self, roles, identity, context=None,
                      stop_on_match=False):
        result = set()
        providers = self.providers
        if not context:
            providers = [p for p in providers if p.contextual is False]

        providers = [p for p in providers
                     if not p.determines or bool(p.determines & roles)]

        for item in providers:
            result |= item.member_subset(roles, identity, context)
            assert not result - roles, \
                    ("Provider %r returned roles %r which "
                     "are not members of the set requested "
                     "(%r)" % (item, result - roles, roles))
            if stop_on_match and result:
                return result

        return result


class StaticRoleProvider(RoleProvider):
    """
    A statically configured role provider
    """

    def __init__(self, user_roles):
        """\
        :param user_roles: a mapping from user identifier to member roles
        """
        self.user_roles = dict((userid, set(roles))
                               for userid, roles in user_roles.items())

    def member_subset(self, roles, identity, context=None):
        return roles & self.user_roles.get(identity, set())


def role_decider(role, contextual=False):
    """
    Function decorator returning a RoleProvider that decides a single role.
    The decorated function should take arguments::

        identity, context=None

    And must return a boolean indicating whether the user has the given role.

    Example:

        from knave.roles import role_decider

        @role_decider('wizard')
        def is_wizard(identity, context):
            return identity in {'gandalf', 'merlin'}

    """

    def role_decider(func):

        class _RoleProvider(RoleProvider):
            """
            Determine whether the user has the single role, ``role``.
            """
            determines = {role}

            def member_subset(self, roles, identity, context=None, role=role,
                              _match=set([role]), _no_match=set(),
                              is_member=func):

                # Short circuit if the query does not concern us
                if role not in roles:
                    return _no_match

                if is_member(identity, context):
                    return _match

                return _no_match

        _RoleProvider.contextual = contextual
        return _RoleProvider()

    return role_decider
