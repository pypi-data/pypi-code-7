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

"""cubicweb-transactionlog specific hooks and operations"""

import cPickle
import zlib
import operator as op

from cubicweb import onevent, Binary, ObjectNotFound, RegistryNotFound
from cubicweb.predicates import is_instance, score_entity
from cubicweb.server.hook import Hook, SingleLastOperation, DataOperationMixIn, match_rtype


class RecordEntity(Hook):
    __regid__ = 'transactionlog.record_entity'
    # give a chance to applicative hooks to transform data
    # (ex. timeseries that setup Binary value from user friendly array)
    order = 999
    # __select__ = computed from registry: setup in registration callback
    events = ('before_update_entity', 'after_add_entity', 'before_delete_entity')
    category = 'transactionlog'

    def __call__(self):
        event = self.event.split('_', 1)[-1] # remove 'before_'
        eid = self.entity.eid
        config = self._cw.vreg['configuration'].select('transactionlog')
        etype = self.entity.cw_etype

        if 'delete' in event:
            try:
                info = config.deleted_entity_info(self._cw, self.entity)
            except:
                info = None
            if info is None:
                return
            SaveLog.get_instance(self._cw).add_data((event, (eid, etype, info)))
            return

        # updated
        edited = self.entity.cw_edited
        try:
            attributes = config.ETYPES[etype] or edited.keys() # XXX
        except:
            return
        schema = self._cw.vreg.schema
        add_data = SaveLog.get_instance(self._cw).add_data

        if 'add' in event:
            if not isinstance(eid, (int, long)):
                raise ValueError(eid)
            SaveLog.get_instance(self._cw).add_data((event, (eid, etype, None)))
            return

        # updated
        for attr in attributes:
            schemaattr = schema[attr]
            if schemaattr.meta: # skip cw meta information
                continue
            if not schemaattr.final:
                continue # inlined are catched by RecordRelation Hook
            old, new = edited.oldnewvalue(attr)
            if old == new:
                continue
            else:
                add_data((event, (eid, etype, (attr, old, new))))


class RecordRelation(Hook):
    __regid__ = 'transactionlog.record_relation'
    # __select__ computed from registrery: setup in registration callback
    events = ('after_add_relation', 'before_delete_relation')
    category = 'transactionlog'

    def __call__(self):
        event = self.event.split('_', 1)[-1] # remove 'before_'
        config = self._cw.vreg['configuration'].select('transactionlog')
        if 'delete' in event:
            data = config.deleted_relation_info(self._cw, self.rtype, self.eidfrom, self.eidto)
        else:
            data = (self.eidfrom, self.eidto)
        if data is not None:
            SaveLog.get_instance(self._cw).add_data((event, (self.rtype, data)))


class SaveLog(DataOperationMixIn, SingleLastOperation):
    containercls = list

    def precommit_event(self):
        data = tuple(self.get_data())
        data = zlib.compress(cPickle.dumps(data))
        self.cnx.create_entity('TransactionLog', data=Binary(data))


def registration_callback(vreg):
    # we need that Configuration implementation is already loaded

    @onevent('after-registry-reload')
    def compute_select():
        try:
            config = vreg['configuration'].select('transactionlog')
        except (ObjectNotFound, RegistryNotFound):
            return # no transactionlog configuration registred

        try:
            if config.ETYPES:
                vreg.register_and_replace(RecordEntity, RecordEntity)

                RecordEntity.__select__ = RecordEntity.__select__ & is_instance(*config.ETYPES.keys())

            if config.RDEFS:
                selectors = (match_rtype(rtype,
                                         frometypes=(frometype,) if frometype else None,
                                         toetypes=(toetype,) if toetype else None)
                             for frometype, rtype, toetype in config.RDEFS)
                RecordRelation.__select__ = Hook.__select__ & reduce(op.or_, selectors)
                vreg.register_and_replace(RecordRelation, RecordRelation)
        except AttributeError:
            print 'critical failure to register transaction log'
            print '(unless this is a "cubicweb-ctl i18ncube" or such command)'
