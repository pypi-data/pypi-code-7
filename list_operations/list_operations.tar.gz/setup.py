from distutils.core import setup

setup (
	name = 'list_operations',
	packages = ['list_operations'],
	version = '0.1',
	author = 'Jana Awada',
	author_email = 'awada_jana@yahoo.com',
	url = 'http://github.com/Jana-A/list_operations/releases',
	description = 'Two functions performed on lists.',
	long_description = """

							-------\ unnest \--------
							Given a list of nested lists and/or nested tuples (a complex nested structure of list/tuples that is not known), the unnest function will extract and return single elements only (strings, floats, integers) that were inside these list and/or tuple structures.

							-------\ list2dict \--------
							Given a list of strings that may or may not be duplicated, the list2dict function outputs a dictionary having keys equal to the unique strings in the list and values equal to the number of times the string is repeated in the list (count).

					   """,	
	classifiers = [
	'Programming Language :: Python',
	'Programming Language :: Python :: 3',
	'License :: OSI Approved :: MIT License',
	'Operating System :: OS Independent'
	]
)
