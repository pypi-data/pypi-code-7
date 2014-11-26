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

"""cubicweb-transactionlog entity's classes"""

import cPickle
import zlib
from logilab.common.registry import RegistrableObject
from cubicweb.entities import AnyEntity
from cubicweb.predicates import is_instance



class TransactionLog(AnyEntity):
    __regid__ = 'TransactionLog'
    __select__ = is_instance('TransactionLog')

    def dump_data(self, data):
        """Dump data into the db"""
        self.cw_set(data=zlib.compress(cPickle.dumps(data)))

    def load_data(self):
        """Load data from the db"""
        return cPickle.loads(zlib.decompress(self.data.getvalue()))


class Configuration(RegistrableObject):
    __registry__ = 'configuration'
    __regid__ = 'transactionlog'
    __abstract__ = True

    ETYPES = {}
    # a dictionary of ``{etype: (attrname1, attrname2, ...)}``.
    # A false value means that all attributes must be watched.
    # ex. {'CWUser': ()} => watch any modification on CWUser
    # ex. {'CWUser': ('login',)} => watch modifications on login only

    RDEFS = ()
    # a tuple of triplets ``(frometype, rtype, toetype)``.
    # ``frometype`` and/or ``toetype`` can be None, meaning that any
    # subject and/or object candidate of ``rtype`` is watched.

    def deleted_entity_info(self, _cnx, entity):
        return entity.dc_title()

    def deleted_relation_info(self, _cnx, rtype, eidfrom, eidto):
        return eidfrom, eidto


def registration_callback(vreg):
    vreg.register(TransactionLog)
