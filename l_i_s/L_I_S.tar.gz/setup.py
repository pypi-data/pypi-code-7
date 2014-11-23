from distutils.core import setup

setup (
	name = 'L_I_S',
	packages = ['L_I_S'],
	version = '0.2',
	author = 'Jana Awada',
	author_email = 'awada_jana@yahoo.com',
	url = 'http://github.com/Jana-A/L_I_S/releases',
	description = 'A function that outputs the longest increasing subsequenes of a list of unique numbers.',
	long_description = """
							-------\ LIS \--------
							This module contains the main function "LIS" plus 2 ad hoc functions used by LIS namely "nest" and "gmls".
							Given a list of unique numbers, the LIS function outputs all LIS from list i.e. the longest increasing subsequences having the maximum length among all results. To implement, type "from L_I_S import LIS" then try "LIS([2,5,1,3,4])". Note that the external module list_operations is required "from list_operations import unnest".
					   """,
	install_requires = ['list_operations.unnest'],
	keywords = ['longest increasing subsequence'],
	classifiers = [
	'Programming Language :: Python',
	'Programming Language :: Python :: 3.3',
	'License :: OSI Approved :: MIT License',
	'Operating System :: OS Independent'
	]
)
