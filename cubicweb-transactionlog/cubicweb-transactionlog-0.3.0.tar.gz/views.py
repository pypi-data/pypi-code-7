# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-transactionlog views/forms/actions/components for web ui"""

import cPickle
import zlib

from logilab.mtconverter import xml_escape

from cwtags.tag import div
 
from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


class TLogOneLine(EntityView):
    __regid__ = 'incontext'
    __select__ = is_instance('TransactionLog')

    def entity_call(self, entity):
        w = self.w
        for line in cPickle.loads(zlib.decompress(entity.data.getvalue())):
            with div(w):
                w(xml_escape(unicode(repr(line))))
