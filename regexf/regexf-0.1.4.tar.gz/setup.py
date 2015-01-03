#https://pypi.python.org/pypi martinmohan/Wai....See..
#python setup.py sdist upload
#python setup.py bdist --help-formats

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
        name='regexf',
        version="0.1.4",
        author='Martin Mohan',
        author_email='martinmohan@yahoo.com',
        packages=['regexf'],
        scripts=['regexf/regexf_test.sh', 'regexf/regexf_unittest.sh', 'regexf/regexf','regexf/regexf.ini','regexf/regexf_test.ini','regexf/regexf_version.py','regexf/assertEqual','regexf/assertGrep','regexf/assertTrue','regexf/assertFalse', 'regexf/assertTest'],
        url='http://pypi.python.org/pypi/regexf/',
        license='LICENSE.txt',
        description='Compare regular expressions against those in a file',
        long_description=open('README').read(),
        install_requires=[
            "ConfigParser",
            ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Programming Language :: Python',
            'Topic :: System',
            'Topic :: Software Development',
            ],

        )
