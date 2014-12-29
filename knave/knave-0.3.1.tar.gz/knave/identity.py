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

__all__ = ['IdentityAdapter', 'RepozeWhoIdentityAdapter',
           'RemoteUserIdentityAdapter']


class IdentityAdapter(object):
    """
    Adapt a WSGI environ dict to an identity as understood by the ACL.
    """

    def __call__(self, environ):
        raise NotImplementedError()

    def is_authenticated(self, environ):
        """
        Return a boolean indicating whether a user is authenticated or not.
        """
        return self(environ) is not None


class RepozeWhoIdentityAdapter(IdentityAdapter):

    def __call__(self, environ):
        identity = environ.get('repoze.who.identity')
        if identity is not None:
            return identity['repoze.who.userid']
        return None


class RemoteUserIdentityAdapter(IdentityAdapter):
    """
    Look for the identity in `environ['REMOTE_USER']`
    """
    def __call__(self, environ):
        return environ.get('REMOTE_USER')
