# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import datetime
from zipfile import ZipFile
from .base import TestBase
from .base import EXIST_DB_URL
import zExceptions

PREFIX = 'testing'


class BasicTests(TestBase):

    def setUp(self):
        handle = self.portal.connector.webdav_handle()
        if handle.exists(PREFIX):
            handle.removedir(PREFIX, False, True)
        handle.makedir(PREFIX)
        handle.makedir(PREFIX + '/foo')
        with handle.open(PREFIX + '/foo/index.html', 'wb') as fp:
            fp.write('<html/>')
        with handle.open(PREFIX + '/foo/index.xml', 'wb') as fp:
            fp.write('<?xml version="1.0" ?>\n<hello>world</hello>')
        self.portal.connector.existdb_subpath = PREFIX

    def tearDown(self):
        self.portal.connector.existdb_subpath = None
        handle = self.portal.connector.webdav_handle()
        if handle.exists(PREFIX):
            handle.removedir(PREFIX, False, True)

    def _get_view(self):
        from zopyx.existdb.browser.connector import Connector as ConnectorView
        from Testing.makerequest import makerequest
        request = makerequest(self.portal)

        class FakeResponse(object):

            def redirect(self, url):
                pass
        request.response = FakeResponse()
        return ConnectorView(request=request, context=self.portal.connector)

    def testCheckPortalType(self):
        assert self.portal.connector.portal_type == 'zopyx.existdb.connector'

    def testCheckWebdavHandle(self):
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(
            handle.url, EXIST_DB_URL + '/exist/webdav/db/{}/'.format(PREFIX))

    def testFileCheck(self):
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('foo/index.html'), True)
        self.assertEqual(handle.exists('foo/index.xml'), True)
        self.assertEqual(handle.exists('foo/xxxx.html'), False)

    def testRenameCollection(self):
        self.login('god')
        view = self._get_view()
        view.rename_collection('', 'foo', 'bar')
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('bar/index.html'), True)
        self.assertEqual(handle.exists('bar/index.xml'), True)

    def testCreateCollection(self):
        self.login('god')
        view = self._get_view()
        view.create_collection('', 'new')
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('new'), True)

    def testRemoveCollection(self):
        self.login('god')
        view = self._get_view()
        view.remove_collection('', 'foo')
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('foo'), False)

    def testZipExport(self):
        self.login('god')
        view = self._get_view()
        fn = view.zip_export(download=False)
        zf = ZipFile(fn, 'r')
        self.assertEqual('foo/index.html' in zf.namelist(), True)
        self.assertEqual('foo/index.xml' in zf.namelist(), True)
        zf.close()
        os.unlink(fn)

    def testZipImport(self):
        self.login('god')
        fn = os.path.join(os.path.dirname(__file__), 'sample.zip')
        view = self._get_view()
        view.zip_import(fn)
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('import/test.xml'), True)
        self.assertEqual(handle.exists('import/test.html'), True)

    def testHumanReadableDatetime(self):
        view = self._get_view()
        now = datetime.datetime.utcnow()
        result = view.human_readable_datetime(now)
        self.assertEqual(result, 'now')

    def testHumanReadableFilesize(self):
        view = self._get_view()
        result = view.human_readable_filesize(1000000)
        self.assertEqual(result, '976 KB')

    def testLogger(self):
        c = self.portal.connector
        self.assertEqual(len(c.logger), 0)
        c.log(u'error', 'error')
        c.log(u'info', 'info')
        self.assertEqual(len(c.logger), 2)
        c.log_clear()
        self.assertEqual(len(c.logger), 0)

    def testTraversalExistingPath(self):
        path = 'connector/@@view/foo/index.html'
        result = self.portal.restrictedTraverse(path)
        # with XML preamble
        self.assertEqual('<html/>' in result.wrapped_object, True)
        self.assertEqual('wrapped_meta' in result.__dict__, True)
        info = result.wrapped_info
        self.assertEqual('modified_time' in info, True)
        self.assertEqual('name' in info, True)
        self.assertEqual('st_mode' in info, True)

    def testTraversalNonExistingPath(self):
        path = 'connector/@@view/foo/doesnotexist.html'
        with self.assertRaises(zExceptions.NotFound):
            self.portal.restrictedTraverse(path)

    def testRenderControlPanel(self):
        with self.assertRaises(zExceptions.Unauthorized):
            view = self.portal.restrictedTraverse('@@existdb-settings')
            result = view()

        self.login('god')
        view = self.portal.restrictedTraverse('@@existdb-settings')
        result = view()

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
