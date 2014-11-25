# Copyright 2014 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the
#    License. You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied. See the License for the specific language
#    governing permissions and limitations under the License.

import unittest

import mock

from evproc import event


class NamespaceTest(unittest.TestCase):
    def test_init(self):
        ns = event.Namespace()

        self.assertEqual(ns._data, {})

    def test_getattr_internal(self):
        ns = event.Namespace()
        ns._data.update({'_internal': 'value'})

        self.assertRaises(AttributeError, lambda: ns._internal)

    def test_getattr_missing(self):
        ns = event.Namespace()

        self.assertRaises(AttributeError, lambda: ns.missing)

    def test_getattr_function(self):
        ns = event.Namespace()
        ns._data.update({'spam': 'value'})

        self.assertEqual(ns.spam, 'value')

    def test_setattr_internal(self):
        ns = event.Namespace()
        ns._data.update({'_internal': 'value'})

        def test_func():
            ns._internal = 'other'

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(ns._data, {'_internal': 'value'})

    def test_setattr_function(self):
        ns = event.Namespace()

        ns.spam = 'value'

        self.assertEqual(ns._data, {'spam': 'value'})

    def test_delattr_internal(self):
        ns = event.Namespace()
        ns._data.update({'_internal': 'value'})

        def test_func():
            del ns._internal

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(ns._data, {'_internal': 'value'})

    def test_delattr_missing(self):
        ns = event.Namespace()
        ns._data.update({'spam': 'value'})

        def test_func():
            del ns.missing

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(ns._data, {'spam': 'value'})

    def test_delattr_function(self):
        ns = event.Namespace()
        ns._data.update({'spam': 'value'})

        del ns.spam

        self.assertEqual(ns._data, {})


class ProcessorDataTest(unittest.TestCase):
    def test_init(self):
        pd = event.ProcessorData()

        self.assertEqual(pd._namespaces, {})

    @mock.patch.object(event, 'Namespace')
    def test_getattr_internal(self, mock_Namespace):
        pd = event.ProcessorData()
        pd._namespaces.update({'_internal': 'namespace'})

        self.assertRaises(AttributeError, lambda: pd._internal)
        self.assertFalse(mock_Namespace.called)
        self.assertEqual(pd._namespaces, {'_internal': 'namespace'})

    @mock.patch.object(event, 'Namespace')
    def test_getattr_missing(self, mock_Namespace):
        pd = event.ProcessorData()

        self.assertEqual(pd.missing, mock_Namespace.return_value)
        mock_Namespace.assert_called_once_with()
        self.assertEqual(pd._namespaces,
                         {'missing': mock_Namespace.return_value})

    @mock.patch.object(event, 'Namespace')
    def test_getattr_function(self, mock_Namespace):
        pd = event.ProcessorData()
        pd._namespaces.update({'spam': 'value'})

        self.assertEqual(pd.spam, 'value')
        self.assertFalse(mock_Namespace.called)
        self.assertEqual(pd._namespaces, {'spam': 'value'})

    def test_setattr(self):
        pd = event.ProcessorData()
        pd._namespaces.update({'spam': 'value'})

        def test_func():
            pd.spam = 'other'

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(pd._namespaces, {'spam': 'value'})

    def test_delattr(self):
        pd = event.ProcessorData()
        pd._namespaces.update({'spam': 'value'})

        def test_func():
            del pd.spam

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(pd._namespaces, {'spam': 'value'})


class EventForTest(event.Event):
    name = 'test'


class EventTest(unittest.TestCase):
    @mock.patch.object(event, 'ProcessorData')
    def test_init_base(self, mock_ProcessorData):
        ev = EventForTest()

        self.assertEqual(ev.ctxt, None)
        self.assertEqual(ev._proc, mock_ProcessorData.return_value)
        mock_ProcessorData.assert_called_once_with()

    @mock.patch.object(event, 'ProcessorData')
    def test_init_alt(self, mock_ProcessorData):
        ev = EventForTest('ctxt')

        self.assertEqual(ev.ctxt, 'ctxt')
        self.assertEqual(ev._proc, mock_ProcessorData.return_value)
        mock_ProcessorData.assert_called_once_with()

    @mock.patch.object(event, 'ProcessorData', return_value='procdata')
    def test_proc(self, mock_ProcessorData):
        ev = EventForTest()

        self.assertEqual(ev.proc, 'procdata')
