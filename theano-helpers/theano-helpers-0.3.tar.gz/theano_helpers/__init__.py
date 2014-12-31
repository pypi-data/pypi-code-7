import pprint
import cStringIO as StringIO
import itertools
from collections import OrderedDict

import theano
import theano.tensor as T
import nested_structures
import pandas as pd
import jinja2
from .template import (OPERATOR_TEMPLATE, FUNCTION_HEADER_TEMPLATE,
                       CYTHON_HEADER_TEMPLATE)


CTYPE_BY_THEANO_TYPE = OrderedDict([('uint8', 'uint8_t'),
                                    ('uint16', 'uint16_t'),
                                    ('uint32', 'uint32_t'),
                                    ('uint64', 'uint64_t'),
                                    ('int8', 'int8_t'),
                                    ('int16', 'int16_t'),
                                    ('int32', 'int32_t'),
                                    ('int64', 'int64_t'),
                                    ('float32', 'float'),
                                    ('float64', 'double')])


def what_am_i(node):
    if node.owner:
        node, args = extract_op(node)
    if isinstance(node, theano.scalar.basic.Mul):
        return 'multiply'
    elif isinstance(node, theano.scalar.basic.IntDiv):
        return 'divide_floor'
    elif isinstance(node, theano.scalar.basic.TrueDiv):
        return 'divide'
    elif isinstance(node, theano.scalar.basic.Add):
        return 'add'
    elif isinstance(node, theano.scalar.basic.Sub):
        return 'subtract'
    elif isinstance(node, theano.tensor.elemwise.DimShuffle):
        return 'broadcast'
    elif isinstance(node, theano.scalar.basic.Pow):
        return 'pow'
    elif isinstance(node, theano.scalar.basic.Sqr):
        return 'sqr'
    elif isinstance(node, theano.scalar.basic.Sqrt):
        return 'sqrt'
    elif isinstance(node, theano.tensor.TensorConstant):
        return node.value
    elif isinstance(node, theano.tensor.TensorVariable):
        return node.name


operation = lambda v: v.owner.op.scalar_op if hasattr(v.owner.op, 'scalar_op') else v.owner.op
arguments = lambda v: v.owner.inputs
extract_op = lambda t: (operation(t), arguments(t)) if t.owner else t
extract_node = lambda t: (t, arguments(t)) if t.owner else t

# TODO:
#
#  - Apply `extract_op` recursively to construct nested operation/argument
#    tree.
#   * Perhaps we can get this in a form that will work with the
#     `nested_structures` Python package.
#  - Generate code for `thrust::transform_iterator` to implement element-wise
#    operator, using names of leaf nodes as `DeviceVectorView` variable names.
#  - Does Theano provide any notation for indirect vector element access,
#    equivalent to `permutation_iterator`?
#   * Yes! See [`TensorVariable.take`][1].
#
# [1]: http://deeplearning.net/software/theano/library/tensor/basic.html#tensor._tensor_py_operators.take
def extract(node):
    try:
        #op, args = extract_op(node)
        op, args = extract_node(node)
        if args is None:
            return op
        else:
            return (op, map(extract, args))
    except (ValueError, TypeError):
        # `node` is a leaf node, *not* an operation.
        return node


class DataFlowGraph(object):
    def __init__(self, operation_graph):
        self.operation_graph = operation_graph
        self.tree = nested_structures.apply_depth_first(
            [extract(operation_graph)], lambda node, *args: node, as_dict=True)

    def collect(self, func=None):
        if func is None:
            func = lambda key, *args: key
        return nested_structures.dict_collect(self.tree, func)

    def flatten(self):
        return self.collect()

    def __str__(self):
        return pprint.pformat(map(what_am_i, self.flatten()))


class Expression(object):
    def __init__(self):
        self.output = StringIO.StringIO()

    def pre(self, v, node, parents, first, last):
        self.output.write('(%s)%s' % (v.type.dtype, what_am_i(v)))
        if node.children is not None:
            self.output.write('(')

    def post(self, v, node, parents, first, last):
        if node.children is not None:
            self.output.write(')')
        if not last:
            self.output.write(', ')


class TypeNames(object):
    def __init__(self, dfg):
        inputs = [n for n in dfg.flatten() if not n.owner]
        self.nodes_by_name = OrderedDict([(n.name, n)
                                          if n.name else
                                          ('iterator_%d' % i, n)
                                          for i, n in
                                          enumerate(dfg.flatten())])
        self.names_by_node = OrderedDict([(node, name)
                                          for name, node in
                                          self.nodes_by_name.iteritems()])
        self.typenames = OrderedDict()
        self.typedefs = OrderedDict()
        self.values = OrderedDict()
        self.handler = OrderedDict()
        for i in inputs:
            self.update(i)

    def __getitem__(self, node):
        return self.typenames[node]

    def __in__(self, node):
        return node in self.typenames

    def handle_scalar(self, node):
        op, args = extract_op(node)
        self.typedefs[node] = ('thrust::constant_iterator<' +
                               self.typenames[args[0]] + ' >')
        name = self.names_by_node[node]
        self.values[node] = '%s(%s)' % (name, args[0])

    def handle_binary(self, node):
        op, args = extract_op(node)
        if isinstance(op, theano.scalar.basic.Mul):
            op_type = ('thrust::multiplies<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, (theano.scalar.basic.TrueDiv,
                             theano.scalar.basic.IntDiv)):
            op_type = ('thrust::divides<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, theano.scalar.basic.Add):
            # 'add'
            op_type = ('thrust::plus<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, theano.scalar.basic.Sub):
            op_type = ('thrust::minus<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, theano.scalar.basic.Pow):
            # 'pow'
            op_type = ('cythrust::power<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, theano.scalar.basic.Sqr):
            # 'sqr'
            op_type = ('cythrust::square<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        elif isinstance(op, theano.scalar.basic.Sqrt):
            op_type = ('cythrust::square_root<' +
                       CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')
        self.typedefs[node] = (
            'thrust::transform_iterator<unpack_binary_args<' + op_type + ' >,'
            'thrust::zip_iterator<'
            'thrust::tuple<' + ', '.join([self.typenames[a] for a in args]) + ' > > >')
        name = self.names_by_node[node]
        self.typenames[node] = '%s_t' % name
        self.values[node] = ('%s(thrust::make_zip_iterator(thrust::make_tuple(%s)), unpack_binary_args<%s >(%s()))'
                             % (name, ', '.join([self.names_by_node[a]
                                                 for a in args]), op_type,
                                op_type))

    def update(self, node):
        if node.owner:
            op, args = extract_op(node)
            if isinstance(op, theano.tensor.elemwise.DimShuffle):
                self.typenames[node] = ('thrust::constant_iterator<' +
                                        self.typenames[args[0]] + ' >')
                self.handle_scalar(node)
            else:
                self.handle_binary(node)
        elif isinstance(node, theano.tensor.TensorVariable):
            dtype = node.dtype + '_t'
            if node.type.ndim == 0:
                self.typenames[node] = dtype
            elif node.type.ndim == 1:
                self.typenames[node] = \
                    'typename thrust::device_vector<%s>::iterator' % dtype
        return self[node]


class ThrustCode(object):
    def __init__(self, dfg):
        self.dfg = dfg
        ordered_nodes = sorted([(depth, node)
                                for node, wrapper, parents, first, last, depth in
                                dfg.collect(lambda *args: args) if node.owner],
                            key=lambda x: -x[0])
        node_data = pd.DataFrame(ordered_nodes, columns=['height', 'node'])

        typenames = TypeNames(dfg)
        node_data['inputs'] = [n.owner.inputs for n in node_data['node']]
        node_data['output'] = [n.owner.out for n in node_data['node']]

        for n in node_data['output']:
            typenames.update(n)
        output_nodes = set(node_data['output'])
        graph_inputs = [n for inputs in node_data['inputs']
                        for n in inputs if n not in output_nodes]

        self.typenames = typenames
        self.output_nodes = output_nodes
        self.graph_inputs = graph_inputs
        self.node_data = node_data

    def iterator_code(self, name):
        iterator_template = jinja2.Template(OPERATOR_TEMPLATE)

        iterator_code = iterator_template.render(name=name,
                                                 typenames=self.typenames,
                                                 graph_inputs=
                                                 self.graph_inputs)
        return iterator_code

    def header_code(self, name):
        header_template = jinja2.Template(FUNCTION_HEADER_TEMPLATE)
        header_code = header_template.render(name=name,
                                             body=self.iterator_code(name))
        return header_code

    def cython_header_code(self, name, header_file):
        cython_header_template = jinja2.Template(CYTHON_HEADER_TEMPLATE)
        return cython_header_template.render(header_file=header_file,
                                             name=name,
                                             graph_inputs=self.graph_inputs,
                                             typenames=self.typenames)


if __name__ == '__main__':
    from path_helpers import path

    pd.set_option('display.width', 300)
    # Example usage
    scalar = T.iscalar('scalar')
    exp = T.scalar('exp', dtype='float32')
    a = T.vector('view1', dtype='uint8')
    b = T.vector('view2', dtype='int32')

    dfg = DataFlowGraph((scalar * a) / (b ** exp))
    thrust_code = ThrustCode(dfg)

    with path('~/local/include/test.hpp').expand().open('wb') as output:
        output.write(thrust_code.header_code('Foo'))
