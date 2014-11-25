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

from evproc import decorator


class WantTest(unittest.TestCase):
    def test_no_filters(self):
        self.assertRaises(TypeError, decorator.want)

    def test_bad_type(self):
        self.assertRaises(TypeError, decorator.want,
                          'one', lambda ev: False, 123)

    def test_one_callable(self):
        filt = mock.Mock()
        func = mock.Mock(spec=[])

        dec = decorator.want(filt)

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_filters, [filt])

    def test_additional_callable(self):
        filt = mock.Mock()
        func = mock.Mock(spec=['_ev_filters'], _ev_filters=['foo'])

        dec = decorator.want(filt)

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_filters, [filt, 'foo'])

    def test_multi_callable(self):
        filts = [
            mock.Mock(return_value=True),
            mock.Mock(return_value=True),
            mock.Mock(return_value=True),
        ]
        func = mock.Mock(spec=[])

        dec = decorator.want(*filts)

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(len(func._ev_filters), 1)
        self.assertTrue(callable(func._ev_filters[0]))
        self.assertNotEqual(func._ev_filters, [filts])
        self.assertNotEqual(func._ev_filters, [filts[0]])

        ev_result = func._ev_filters[0]('ev')

        self.assertEqual(ev_result, True)
        for filt in filts:
            filt.assert_called_once_with('ev')

    def test_multi_callable_short_circuit(self):
        filts = [
            mock.Mock(return_value=True),
            mock.Mock(return_value=False),
            mock.Mock(return_value=True),
        ]
        func = mock.Mock(spec=[])

        dec = decorator.want(*filts)

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(len(func._ev_filters), 1)
        self.assertTrue(callable(func._ev_filters[0]))
        self.assertNotEqual(func._ev_filters, [filts])
        self.assertNotEqual(func._ev_filters, [filts[0]])

        ev_result = func._ev_filters[0]('ev')

        self.assertEqual(ev_result, False)
        filts[0].assert_called_once_with('ev')
        filts[1].assert_called_once_with('ev')
        self.assertFalse(filts[2].called)

    def test_name_filter(self):
        evs = [
            mock.Mock(expected=True, ev_name='ev1'),
            mock.Mock(expected=False, ev_name='ev2'),
            mock.Mock(expected=True, ev_name='ev3'),
        ]
        for ev in evs:
            ev.name = ev.ev_name
        func = mock.Mock(spec=[])

        dec = decorator.want('ev1', 'ev3')

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(len(func._ev_filters), 1)
        self.assertTrue(callable(func._ev_filters[0]))

        for ev in evs:
            ev_result = func._ev_filters[0](ev)

            self.assertEqual(ev_result, ev.expected)

    def test_full_function(self):
        filts = [
            mock.Mock(return_value=True),
            'ev1',
            mock.Mock(side_effect=lambda ev: ev.match),
            'ev3',
            mock.Mock(return_value=True),
        ]
        evs = [
            mock.Mock(expected=True, match=True, ev_name='ev1',
                      filts=set([0, 2, 4])),
            mock.Mock(expected=False, match=True, ev_name='ev2',
                      filts=set()),
            mock.Mock(expected=True, match=True, ev_name='ev3',
                      filts=set([0, 2, 4])),
            mock.Mock(expected=False, match=False, ev_name='ev3',
                      filts=set([0, 2])),
        ]
        for ev in evs:
            ev.name = ev.ev_name
        func = mock.Mock(spec=[])

        dec = decorator.want(*filts)

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(len(func._ev_filters), 1)
        self.assertTrue(callable(func._ev_filters[0]))

        for ev in evs:
            # Reset the filter mocks
            for filt in filts:
                if callable(filt):
                    filt.reset_mock()

            ev_result = func._ev_filters[0](ev)

            self.assertEqual(ev_result, ev.expected)

            # Check that the filters were called
            for idx, filt in enumerate(filts):
                if not callable(filt):
                    continue

                # Was it to be called?
                if idx in ev.filts:
                    filt.assert_called_once_with(ev)
                else:
                    self.assertFalse(filt.called)


class RequiresTest(unittest.TestCase):
    def test_no_procs(self):
        self.assertRaises(TypeError, decorator.requires)

    def test_function(self):
        func = mock.Mock(spec=[])

        dec = decorator.requires('a', 'b', 'c')

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_requires, set(['a', 'b', 'c']))

    def test_addition(self):
        func = mock.Mock(spec='_ev_requires', _ev_requires=set(['d', 'e']))

        dec = decorator.requires('a', 'b', 'c')

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_requires, set(['a', 'b', 'c', 'd', 'e']))


class RequiredByTest(unittest.TestCase):
    def test_no_procs(self):
        self.assertRaises(TypeError, decorator.required_by)

    def test_function(self):
        func = mock.Mock(spec=[])

        dec = decorator.required_by('a', 'b', 'c')

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_required_by, set(['a', 'b', 'c']))

    def test_addition(self):
        func = mock.Mock(spec='_ev_required_by',
                         _ev_required_by=set(['d', 'e']))

        dec = decorator.required_by('a', 'b', 'c')

        self.assertTrue(callable(dec))

        result = dec(func)

        self.assertEqual(result, func)
        self.assertEqual(func._ev_required_by, set(['a', 'b', 'c', 'd', 'e']))
