__version__ = '0.12'

import xmltodict
import copy
import csv


def _process_level(data, parents, result):
    if type(data) is xmltodict.OrderedDict:
        for tag, val in data.items():
            _parents = copy.copy(parents)
            if tag not in ['#text', '@code']:
                _parents.append(tag)
            _process_level(val, _parents, result)
    elif type(data) is list:
        i = 0
        for val in data:
            _parents = copy.copy(parents)
            _parents.append('[%s]' % i)
            _process_level(val, _parents, result)
            i += 1
    else:
        result['_'.join(parents)] = data


def parse_ordered_dict(ordered_dict, out_file=None):
    result = {}

    _process_level(ordered_dict, [], result)

    if out_file:
        with open(out_file, 'wb') as f:
            w = csv.DictWriter(f, result.keys())
            w.writeheader()
            w.writerow(result)
    else:
        return result


def parse_blob(blob, out_file=None):
    return parse_ordered_dict(xmltodict.parse(blob), out_file)


def parse_file(in_file, out_file=None):
    with open(in_file, 'r') as f:
        blob = f.read()
        return parse_blob(blob, out_file)



