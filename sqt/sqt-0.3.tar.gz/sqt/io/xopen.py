"""
Open compressed files transparently.
"""
import gzip

__author__ = 'Marcel Martin'

import sys
if sys.version > '3':
	basestring = str
	from codecs import getreader, getwriter


def xopen(filename, mode='r'):
	"""
	Replacement for the "open" function that can also open
	files that have been compressed with gzip. If the filename ends with .gz,
	the file is opened with gzip.open(). If it doesn't, the regular open()
	is used. If the filename is '-', standard output (mode 'w') or input
	(mode 'r') is returned.
	
	mode can be: 'rt', 'rb', 'wt', or 'wb'
	Instead of 'rt' and 'wt', 'r' and 'w' can be used as abbreviations.
	"""
	if mode == 'r':
		mode = 'rt'
	elif mode == 'w':
		mode = 'wt'
	if mode not in ('rt', 'rb', 'wt', 'wb'):
		raise ValueError("mode '{0}' not supported".format(mode))
	if not isinstance(filename, basestring):
		raise ValueError("the filename must be a string")
	
	# standard input and standard output handling
	if filename == '-':
		if sys.version < '3':
			return sys.stdin if 'r' in mode else sys.stdout
		if mode == 'rt':
			return sys.stdin
		if mode == 'wt':
			return sys.stdout
		if mode == 'rb':
			return sys.stdin.buffer
		if mode == 'wb':
			return sys.stdout.buffer
	if filename.endswith('.gz'):
		if sys.version < '3':
			return gzip.open(filename, mode)
		if mode == 'rt':
			return getreader('utf-8')(gzip.open(filename, 'rb'))
		if mode == 'wt':
			return getwriter('utf-8')(gzip.open(filename, 'wb'))
		if mode == 'rb':
			return gzip.open(filename, mode)
		if mode == 'wt':
			return gzip.open(filename, mode)
	return open(filename, mode)
