#
# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
""" Configuration of installation and service
"""

NO_DEFAULT = object()


class Definition(object):
    def __init__(self, name, kind, secret, default=NO_DEFAULT):
        self.name = name
        self.kind = kind
        self.secret = secret
        self.default = default

    def as_tuple(self):
        return self.name, self.kind, self.secret, self.default

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __repr__(self):
        return 'Definition(%r, %r, %r, %r, %r)' % self.as_tuple()
