"""template automatic tests"""

from datetime import timedelta

from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools.testlib import CubicWebTC, AutomaticWebTest
from cubicweb.devtools.fill import ValueGenerator

class SchemaTC(CubicWebTC):
    def test(self):
        req = self.request()
        wo = req.create_entity('WorkOrder', title=u'hop')
        wo.cw_unrelated_rql('todo_by', 'Resource', 'subject')

class TimeSheetValueGenerator(ValueGenerator):

    def generate_Calendaruse_stop(self, entity, index):
        return entity.start + timedelta(days=2)

    def generate_Timeperiod_stop(self, entity, index):
        return entity.start + timedelta(days=2)

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Activity', 'Resource', 'Resourcetype'))

    def list_startup_views(self):
        # XXX needs to specify req.form['project'| 'workcase'] to test
        # [prj-]acstats views
        return ('index',) # 'actstats', 'prj-actstats'

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
