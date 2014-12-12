# -*- coding: utf-8 -*-
#
# Copyright 2014 Danny Goodall
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Taken from Rotem Yaari's munch module"""
import sys

_PY2 = (sys.version_info < (3,0))

identity = lambda x : x

# u('string') replaces the forwards-incompatible u'string'
if _PY2:
    import codecs
    def u(string):
        return codecs.unicode_escape_decode(string)[0]
else:
    u = identity

# dict.iteritems(), dict.iterkeys() is also incompatible
if _PY2:
    iteritems = dict.iteritems
    iterkeys = dict.iterkeys
else:
    iteritems = dict.items
    iterkeys  = dict.keys