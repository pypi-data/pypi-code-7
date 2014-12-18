from __future__ import division
import itertools as it
import psutil
from collections import OrderedDict, namedtuple

data_type = namedtuple('data_type', ['new_name', 'category'])
SCHEMA = OrderedDict([
    ('user', data_type('user_time', 'cpu_times')),
    ('system', data_type('system_time', 'cpu_times')),
    ('rss', data_type('rss_mem_kb', 'memory_info')),
    ('vms', data_type('vms_mem_kb', 'memory_info')),
    ('read_count', data_type('read_count', 'io_counters')),
    ('read_bytes', data_type('io_read_kb', 'io_counters')),
    ('write_bytes', data_type('io_write_kb', 'io_counters')),
    ('write_count', data_type('io_write_count', 'io_counters')),
    ('num_fds', data_type('num_fds', 'num_fds')),
    ('voluntary', data_type('ctx_switch_voluntary', 'num_ctx_switches')),
    ('involuntary', data_type('ctx_switch_involuntary', 'num_ctx_switches')),
    ('num_threads', data_type('num_threads', 'num_threads')),
])

def mean(values):
    n = 0.0
    total = 0.0
    for v in values:
        if v is not None:
            total += v
            n += 1
    if n == 0:
        return 0
    else:
        return int(total / n)

_max = max
def max(values):
    try:
        return _max(values)
    except ValueError:
        return 0


def _poll(proc):
    """
    Polls a process
    :yields: (attribute_name, value)
    """

    def _human_readable(field, value):
        new_name = SCHEMA[field].new_name
        if 'kb' in new_name:
            value = int(value / 1024.)
        return new_name, value


    attrs = ['cpu_times', 'memory_info', 'io_counters', 'num_fds', 'num_ctx_switches', 'num_threads']
    for category in attrs:
        try:
            r = getattr(proc, 'get_' + category)()
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:
            continue
        except AttributeError:
            continue

        if hasattr(r, '_fields'):
            for field in r._fields:
                value = getattr(r, field)
                yield _human_readable(field, value)
        else:
            field, value = category, r
            yield _human_readable(field, value)


def poll_children(p):
    """
    :yields: (attribute_name, the sum of all polled values of a process and it's children)
    """
    polls = (_poll(child) for child in it.chain(p.get_children(recursive=True), [p]))
    for tuples in it.izip(*polls):
        name = tuples[0][0]
        yield name, sum(value for _, value in tuples)

def which(program):
    #http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None