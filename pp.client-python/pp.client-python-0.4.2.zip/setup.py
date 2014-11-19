import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'docs', 'source', 'README.rst')).read()
CHANGES = open(os.path.join(here,  'docs', 'source','CHANGES.rst')).read()

requires = [
    'setuptools',
    'requests',
    'logbook',
    'plac',
]

setup(name='pp.client-python',
      version='0.4.2',
      description='Produce & Publish Python Client',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/pp.client-python',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['pp', 'pp.client', 'pp.client.python'],
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pp.server",
      entry_points="""\
      [console_scripts]
      pp-unoconv=pp.client.python.unoconv:main
      pp-pdf=pp.client.python.pdf:main
      pp-poll=pp.client.python.poll:main
      pp-version=pp.client.python.version:main
      pp-converters=pp.client.python.converter:main
      """,
      )
