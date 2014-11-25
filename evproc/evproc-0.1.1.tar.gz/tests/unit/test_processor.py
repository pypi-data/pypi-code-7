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

from evproc import exc
from evproc import processor


class TopoSortTest(unittest.TestCase):
    def test_sorted(self):
        nodes_map = {
            'node0': mock.Mock(test_reqs=set()),
            'node1': mock.Mock(test_reqs=set(['node0'])),
            'node2': mock.Mock(test_reqs=set(['node0', 'node1'])),
            'node3': mock.Mock(test_reqs=set(['node2'])),
            'node4': mock.Mock(test_reqs=set(['node1', 'node3'])),
        }
        for name, node in nodes_map.items():
            node.name = name
            node.reqs = set(nodes_map[name] for name in node.test_reqs)

        result = list(processor._topo_sort(set(nodes_map.values())))

        self.assertEqual(result, [nodes_map['node%d' % i] for i in range(5)])

    def test_loop(self):
        nodes_map = {
            'node0': mock.Mock(test_reqs=set(['node4'])),
            'node1': mock.Mock(test_reqs=set(['node0'])),
            'node2': mock.Mock(test_reqs=set(['node0', 'node1'])),
            'node3': mock.Mock(test_reqs=set(['node2'])),
            'node4': mock.Mock(test_reqs=set(['node1', 'node3'])),
        }
        for name, node in nodes_map.items():
            node.name = name
            node.reqs = set(nodes_map[name] for name in node.test_reqs)

        self.assertRaises(exc.IncompatibleRequirementsException, list,
                          processor._topo_sort(set(nodes_map.values())))


class ProcNodeTest(unittest.TestCase):
    def test_init(self):
        pn = processor.ProcNode('proc', 'name')

        self.assertEqual(pn.proc, 'proc')
        self.assertEqual(pn.name, 'name')
        self.assertEqual(pn._func, None)
        self.assertEqual(pn.filters, [])
        self.assertEqual(pn.reqs, set())

    def test_hash(self):
        pn = processor.ProcNode('proc', 'name')

        self.assertEqual(hash(pn), hash('name'))

    def test_eq(self):
        pn1 = processor.ProcNode('proc', 'name')
        pn2 = processor.ProcNode('proc', 'name')
        pn3 = processor.ProcNode('proc', 'other')

        self.assertTrue(pn1 == pn1)
        self.assertTrue(pn1 == pn2)
        self.assertFalse(pn1 == pn3)

    def test_ne(self):
        pn1 = processor.ProcNode('proc', 'name')
        pn2 = processor.ProcNode('proc', 'name')
        pn3 = processor.ProcNode('proc', 'other')

        self.assertFalse(pn1 != pn1)
        self.assertFalse(pn1 != pn2)
        self.assertTrue(pn1 != pn3)

    def test_call(self):
        pn = processor.ProcNode('proc', 'name')
        pn._func = mock.Mock()

        result = pn('ev')

        self.assertEqual(result, pn._func.return_value)
        pn._func.assert_called_once_with('proc', 'ev')

    def test_check_nofilts(self):
        pn = processor.ProcNode('proc', 'name')

        result = pn.check('ev')

        self.assertTrue(result)

    def test_check_filts_false(self):
        filts = [
            mock.Mock(return_value=False),
            mock.Mock(return_value=False),
            mock.Mock(return_value=False),
            mock.Mock(return_value=False),
        ]
        pn = processor.ProcNode('proc', 'name')
        pn.filters = filts

        result = pn.check('ev')

        self.assertFalse(result)
        for filt in filts:
            filt.assert_called_once_with('ev')

    def test_check_filts_true(self):
        filts = [
            mock.Mock(return_value=False, expected=True),
            mock.Mock(return_value=False, expected=True),
            mock.Mock(return_value=True, expected=True),
            mock.Mock(return_value=False, expected=False),
        ]
        pn = processor.ProcNode('proc', 'name')
        pn.filters = filts

        result = pn.check('ev')

        self.assertTrue(result)
        for filt in filts:
            if filt.expected:
                filt.assert_called_once_with('ev')
            else:
                self.assertFalse(filt.called)

    def test_func_get(self):
        pn = processor.ProcNode('proc', 'name')
        pn._func = 'func'

        self.assertEqual(pn.func, 'func')

    def test_func_set_twice(self):
        proc = mock.Mock(**{'_get.return_value': None})
        func = mock.Mock(_ev_filters=[], _ev_requires=[], _ev_required_by=[])
        pn = processor.ProcNode(proc, 'name')
        pn._func = 'func'

        def test_func():
            pn.func = func

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(pn._func, 'func')
        self.assertEqual(pn.filters, [])
        self.assertEqual(pn.reqs, set())
        self.assertFalse(proc._get.called)

    def test_func_set(self):
        reqs = {
            'req1': mock.Mock(),
            'req2': mock.Mock(),
            'req3': mock.Mock(),
            'req_by1': mock.Mock(reqs=set()),
            'req_by2': mock.Mock(reqs=set()),
            'req_by3': mock.Mock(reqs=set()),
        }
        proc = mock.Mock(**{'_get.side_effect': lambda x: reqs[x]})
        func = mock.Mock(
            _ev_filters=['filt1', 'filt2', 'filt3'],
            _ev_requires=['req1', 'req2', 'req3'],
            _ev_required_by=['req_by1', 'req_by2', 'req_by3'],
        )
        pn = processor.ProcNode(proc, 'name')

        pn.func = func

        self.assertEqual(pn._func, func)
        self.assertEqual(pn.filters, ['filt1', 'filt2', 'filt3'])
        self.assertEqual(pn.reqs,
                         set([reqs['req1'], reqs['req2'], reqs['req3']]))
        self.assertEqual(reqs['req_by1'].reqs, set([pn]))
        self.assertEqual(reqs['req_by2'].reqs, set([pn]))
        self.assertEqual(reqs['req_by3'].reqs, set([pn]))
        proc._get.assert_has_calls([
            mock.call('req1'),
            mock.call('req2'),
            mock.call('req3'),
            mock.call('req_by1'),
            mock.call('req_by2'),
            mock.call('req_by3'),
        ])
        self.assertEqual(proc._get.call_count, 6)

    def test_func_delete(self):
        pn = processor.ProcNode('proc', 'name')
        pn._func = 'func'

        def test_func():
            del pn.func

        self.assertRaises(AttributeError, test_func)
        self.assertEqual(pn._func, 'func')


class ProcessorTest(unittest.TestCase):
    def test_init(self):
        proc = processor.Processor()

        self.assertEqual(proc.nodes, {})
        self.assertEqual(proc.topo_cache, {})

    @mock.patch.object(processor, 'ProcNode', side_effect=lambda x, y: y)
    def test_get_exists(self, mock_ProcNode):
        proc = processor.Processor()
        proc.nodes['spam'] = 'node'

        result = proc._get('spam')

        self.assertEqual(result, 'node')
        self.assertEqual(proc.nodes, {'spam': 'node'})
        self.assertFalse(mock_ProcNode.called)

    @mock.patch.object(processor, 'ProcNode', side_effect=lambda x, y: y)
    def test_get_new(self, mock_ProcNode):
        proc = processor.Processor()

        result = proc._get('spam')

        self.assertEqual(result, 'spam')
        self.assertEqual(proc.nodes, {'spam': 'spam'})
        mock_ProcNode.assert_called_once_with(proc, 'spam')

    @mock.patch.object(processor, '_topo_sort', return_value=['a', 'b', 'c'])
    def test_get_procs_cached(self, mock_topo_sort):
        nodes = {
            'node0': mock.Mock(**{'check.return_value': True}),
            'node1': mock.Mock(**{'check.return_value': True}),
            'node2': mock.Mock(**{'check.return_value': False}),
            'node3': mock.Mock(**{'check.return_value': True}),
        }
        for name, node in nodes.items():
            node.name = name
        proc = processor.Processor()
        proc.nodes = nodes
        proc.topo_cache = {
            frozenset(['node0', 'node1', 'node3']): 'cached',
        }

        result = proc._get_procs('ev')

        self.assertEqual(result, 'cached')
        self.assertEqual(proc.topo_cache, {
            frozenset(['node0', 'node1', 'node3']): 'cached',
        })
        self.assertFalse(mock_topo_sort.called)
        for node in nodes.values():
            node.check.assert_called_once_with('ev')

    @mock.patch.object(processor, '_topo_sort', return_value=['a', 'b', 'c'])
    def test_get_procs_uncached(self, mock_topo_sort):
        nodes = {
            'node0': mock.Mock(**{'check.return_value': True}),
            'node1': mock.Mock(**{'check.return_value': True}),
            'node2': mock.Mock(**{'check.return_value': False}),
            'node3': mock.Mock(**{'check.return_value': True}),
        }
        for name, node in nodes.items():
            node.name = name
        proc = processor.Processor()
        proc.nodes = nodes

        result = proc._get_procs('ev')

        self.assertEqual(result, ['a', 'b', 'c'])
        self.assertEqual(proc.topo_cache, {
            frozenset(['node0', 'node1', 'node3']): ['a', 'b', 'c'],
        })
        mock_topo_sort.assert_called_once_with(set([
            nodes['node0'], nodes['node1'], nodes['node3'],
        ]))
        for node in nodes.values():
            node.check.assert_called_once_with('ev')

    @mock.patch.object(processor.Processor, '_get',
                       return_value=mock.Mock(spec=['func'], func=None))
    def test_register_noname(self, mock_get):
        func = mock.Mock(__name__='proc_a')
        node = mock_get.return_value
        proc = processor.Processor()
        proc.topo_cache = {'spam': 'sorted'}

        proc.register(func)

        self.assertEqual(proc.topo_cache, {})
        self.assertEqual(node.func, func)
        mock_get.assert_called_once_with('proc_a')

    @mock.patch.object(processor.Processor, '_get',
                       return_value=mock.Mock(spec=['func'], func=None))
    def test_register_withname(self, mock_get):
        func = mock.Mock(__name__='proc_a')
        node = mock_get.return_value
        proc = processor.Processor()
        proc.topo_cache = {'spam': 'sorted'}

        proc.register(func, 'proc_b')

        self.assertEqual(proc.topo_cache, {})
        self.assertEqual(node.func, func)
        mock_get.assert_called_once_with('proc_b')

    @mock.patch.object(processor.Processor, '_get',
                       return_value=mock.Mock(spec=['func'], func='func'))
    def test_register_exists(self, mock_get):
        func = mock.Mock(__name__='proc_a')
        node = mock_get.return_value
        proc = processor.Processor()
        proc.topo_cache = {'spam': 'sorted'}

        self.assertRaises(exc.ProcessorReregisterException, proc.register,
                          func)
        self.assertEqual(proc.topo_cache, {'spam': 'sorted'})
        self.assertEqual(node.func, 'func')
        mock_get.assert_called_once_with('proc_a')

    @mock.patch.object(processor.Processor, 'register')
    @mock.patch('stevedore.ExtensionManager')
    def test_load_from(self, mock_ExtensionManager, mock_register):
        exts = []
        for i in range(5):
            ext = mock.Mock(plugin='plug%d' % i)
            ext.name = 'ext%d' % i
            exts.append(ext)
        mock_ExtensionManager.return_value = exts
        proc = processor.Processor()

        proc.load_from('name.space')

        mock_ExtensionManager.assert_called_once_with('name.space')
        mock_register.assert_has_calls([
            mock.call('plug%d' % i, 'ext%d' % i) for i in range(5)
        ])
        self.assertEqual(mock_register.call_count, 5)

    @mock.patch.object(processor.Processor, '_get_procs')
    def test_process_base(self, mock_get_procs):
        nodes = [
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        ]
        mock_get_procs.return_value = nodes
        proc = processor.Processor()

        result = proc.process('ev')

        self.assertEqual(result, None)
        mock_get_procs.assert_called_once_with('ev')
        for node in nodes:
            node.assert_called_once_with('ev')

    @mock.patch.object(processor.Processor, '_get_procs')
    def test_process_stop(self, mock_get_procs):
        nodes = [
            mock.Mock(),
            mock.Mock(),
            mock.Mock(side_effect=exc.StopProcessing('stop')),
            mock.Mock(),
        ]
        mock_get_procs.return_value = nodes
        proc = processor.Processor()

        result = proc.process('ev')

        self.assertEqual(result, 'stop')
        mock_get_procs.assert_called_once_with('ev')
        for node in nodes[:-1]:
            node.assert_called_once_with('ev')
        self.assertFalse(nodes[-1].called)
