"""
csample: Hash-based sampling library for Python
"""
from __future__ import division
import argparse
import six
import sys
import xxhash
import spooky


def main():
    parser = argparse.ArgumentParser(description='Perform hash-based filtering')
    parser.add_argument('-r', '--rate', type=float, required=True, help='sampling rate from 0.0 to 1.0')
    parser.add_argument('-s', '--salt', type=str, default='DEFAULT_SALT', help='salt for hash function')
    parser.add_argument('-c', '--col', type=int, default=-1, help='column index (starts from 0)')
    parser.add_argument('--hash', type=str, default='xxhash32', help='hash function: xxhash32 (default), spooky32')
    parser.add_argument('--sep', type=str, default=',', help='column separator')

    args = parser.parse_args()
    rate = args.rate
    salt = args.salt
    col = args.col
    hashfunc = args.hash
    sep = six.u(args.sep)
    if col == -1:
        stream = sample_line(sys.stdin, rate, funcname=hashfunc, salt=salt)
    else:
        tuples = (line.split(sep) for line in sys.stdin)
        stream = (
            sep.join(output)
            for output in sample_tuple(tuples, rate, col, funcname=hashfunc, salt=salt)
        )

    for line in stream:
        sys.stdout.write(line)


def sample_tuple(s, rate, col, funcname='xxhash32', salt='DEFAULT_SALT'):
    """Sample tuples in given stream `s`.

    Performs hash-based sampling with given sampling `rate` by applying a hash
    function `funcname`. Sampling with the same `salt` (or seed) always yields
    result.

    Following example shows how to sample approximately 50% of log data based
    on user ID column. Note that the returned value is a generator:

    >>> logs = (
    ...     # user id, event type, timestamp
    ...     ('alan', 'event a', 0),
    ...     ('alan', 'event b', 1),
    ...     ('brad', 'event a', 2),
    ...     ('cate', 'event a', 3),
    ...     ('cate', 'event a', 4),
    ...     ('brad', 'event b', 5),
    ...     ('brad', 'event c', 6),
    ... )
    >>> list(sample_tuple(logs, 0.5, 0))
    [('brad', 'event a', 2), ('brad', 'event b', 5), ('brad', 'event c', 6)]

    :param s: stream of tuples
    :param rate: sampling rate
    :param col: index of column to be hashed
    :param funcname: name of hash function: xxhash32 (default), spooky
    :param salt: salt or seed for hash function
    :return: sampled stream of tuples
    """
    func = _hash_with_salt(funcname, salt)
    return (l for l in s if func(l[col]) < rate)


def sample_line(s, rate, funcname='xxhash32', salt='DEFAULT_SALT'):
    """Sample strings in given stream `s`.

    The function expects strings instead of tuples, except for that the
    function does the exactly same thing with `sample_tuple()`.

    :param s: stream of strings
    :param rate: sampling rate
    :param funcname: name of hash function: xxhash32 (default), spooky
    :param salt: salt of seed for hash function
    :return: sample stream of strings
    """
    func = _hash_with_salt(funcname, salt)
    return (l for l in s if func(l) < rate)


def _hash_with_salt(funcname, salt):
    seed = xxhash.xxh32(salt).intdigest()

    if funcname == 'xxhash32':
        return lambda x: xxhash.xxh32(x, seed=seed).intdigest() / 0xFFFFFFFF
    elif funcname == 'spooky32':
        return lambda x: spooky.hash32(x, seed=seed) / 0xFFFFFFFF
    else:
        raise ValueError('Unknown function name: %s' % funcname)


if __name__ == '__main__':
    main()
