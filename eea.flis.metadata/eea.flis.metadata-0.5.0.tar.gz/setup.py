import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='eea.flis.metadata',
    version='0.5.0',
    packages=['flis_metadata',
              'flis_metadata.client',
              'flis_metadata.client.management',
              'flis_metadata.client.management.commands',
              'flis_metadata.common',
              'flis_metadata.common.migrations',
              'flis_metadata.common.south_migrations'],
    install_requires=['requests',
                      'django'],
    include_package_data=True,
    license='BSD License',
    description='EEA Metadata models replication support',
    long_description=README,
    author='Mihai Bivol',
    url='https://github.com/eea/flis.metadata',
    author_email='mm.bivol@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
