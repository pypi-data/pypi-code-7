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

__all__ = ['Unauthorized', 'Predicate', 'make_predicate', 'Not', 'Any', 'All']


class Unauthorized(Exception):
    """
    Exception raised to indicate an unauthorized access attempt.

    Normally this would be caught by WSGI middleware and converted to a `401
    Unauthorized` response.
    """


class Predicate(object):

    def __call__(self, acl, identity, context=None):
        """
        Return the result of evaluating the predicate in the WSGI request
        context

        :param acl: The ACL object
        :rtype: bool
        """
        raise NotImplementedError

    def __invert__(self):
        return Not(self)


def make_predicate(func):
    """
    Return a Predicate object that evaluates the given function

    :param func: a function that takes arguments
                 ``(acl, identity, context)`` and returns a boolean.
    :return: a :class:`knave.predicates.Predicate` instance
    """
    class FunctionPredicate(Predicate):
        def __call__(self, acl, identity, context=None):
            return func(acl, identity, context)
    return FunctionPredicate()


class Not(Predicate):

    def __init__(self, other):
        self.predicate = other

    def __call__(self, acl, identity, context=None):
        return not self.predicate(acl, identity, context)


class CompoundPredicate(Predicate):
    """\
    A predicate formed of multiple sub-predicates
    """

    aggregate_func = None

    def __init__(self, *predicates):
        self.predicates = predicates

    def __call__(self, acl, identity, context=None):
        return self.aggregate_func(p(acl, identity, context)
                                   for p in self.predicates)


class All(CompoundPredicate):
    aggregate_func = all


class Any(CompoundPredicate):
    aggregate_func = any
