#!/usr/bin/env python

import argparse
import luxem
import sys
import itertools

def main():
    parser = argparse.ArgumentParser(
        description='Extracts specified elements from luxem documents.',
        epilog='PATH FORMATTING: The path is a list of child selections, starting from the array at the root of the document.  Array selectors can be numbers, (*) (a wildcard, which follows all array children), (range) [X,Y] (a range selection, which follows all children at indexes [X,Y)), or an array of selectors.  Object selectors can be strings, (*) (a wildcard, which follows all object children), or an array of selectors.  Example (you may have to provide shell escapes): luxemx \'(*),file_info,[path,altpath]\''
    )
    parser.add_argument('path', nargs='*', help='A luxem array containing the path to the nodes to output.')
    parser.add_argument('-i', '--infile', nargs=1, type=argparse.FileType('r'), default=sys.stdin, help='File to parse; defaults to stdin.')
    parser.add_argument('-o', '--outfile', nargs=1, type=argparse.FileType('w'), default=sys.stdout, help='File to write to; defaults to stdout.')
    parser.add_argument('-l', '--lines', action='store_true', help='Output only primitives, one per line.')
    parser.add_argument('-p', '--pretty', nargs='?', help='Prettify output with PRETTY tab indentation.  Defaults to 1 tab indent.')
    parser.add_argument('-s', '--pretty-spaced', nargs='?', help='Prettify output with PRETTY_SPACED space indentation.  Defaults to 4 space indent.')
    args = parser.parse_args()

    path = luxem.read_struct(''.join(args.path))

    if not args.strings:
        writer = luxem.Writer(args.outfile)
    else:
        writer = None

    def write(child):
        if isinstance(child, luxem.Reader):
            return
        def true_write(child):
            if writer is None:
                if isinstance(child, basestring):
                    args.outfile.write(child)
                    args.outfile.write('\n')
            else:
                writer.value(child)
        luxem.build_struct(child, lambda x: true_write(x))

    def descend_array(array_context, path):
        wrapped_path = [path]
        path_next = next(wrapped_path[0], None)
        if path_next is None:
            write(array_context)
            return
        def int_comparison(value):
            int_value = int(value)
            return lambda x: x == int_value
        def build_comparison(value):
            if isinstance(value, luxem.Typed):
                if value.name == '*':
                    return lambda x: True
                elif value.name == 'range':
                    low = int(value.value[0])
                    high = int(value.value[1])
                    return lambda x: low <= x < high
                else:
                    raise TypeError('Unknown array path element type: {}'.format(value.name))
            else:
                return int_comparison(value)
        if isinstance(path_next, list):
            comparisons = map(build_comparison, path_next)
        else:
            comparisons = [build_comparison(path_next)]
        state = {
            'count': 0,
        }
        def callback(child):
            if any([comparison(state['count']) for comparison in comparisons]):
                split_iter = itertools.tee(wrapped_path[0])
                wrapped_path[0] = split_iter[0]
                descend(child, split_iter[1])
            state['count'] += 1
        array_context.element(callback)

    def descend_object(object_context, path):
        wrapped_path = [path]
        path_next = next(path, None)
        if path_next is None:
            write(object_context)
            return
        def str_comparison(value):
            return lambda x: x == value
        def build_comparison(value):
            if isinstance(value, luxem.Typed):
                if value.name == '*':
                    return lambda x: True
                else:
                    raise TypeError('Unknown object path element type: {}'.format(value.name))
            else:
                return str_comparison(value)
        if isinstance(path_next, list):
            comparisons = map(build_comparison, path_next)
        else:
            comparisons = [build_comparison(path_next)]
        def callback(key, child):
            if any([comparison(key) for comparison in comparisons]):
                split_iter = itertools.tee(wrapped_path[0])
                wrapped_path[0] = split_iter[0]
                descend(child, split_iter[1])
        object_context.passthrough(callback)

    def descend(child, path):
        if isinstance(child, luxem.Typed):
            child_type = child.name
            child_value = child.value
        else:
            child_value = child
        if isinstance(child_value, (luxem.Reader.Array, luxem.Reader)):
            descend_array(child, path)
        elif isinstance(child_value, luxem.Reader.Object):
            descend_object(child, path)
        else:
            if next(path, None) is None:
                write(child)

    reader = luxem.Reader()
    descend(reader, iter(path))
    reader.feed(args.infile)

main()

