import os
import sys
import re

if sys.version_info[:2] != (3, 4):
    print('Python version >= 3.4 required!', file=sys.stderr)
    sys.exit(1)

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    # binary packages require some additional packages installed on your system like gcc
    'Pillow==2.5.2',
    'lxml==3.3.5',
    'pyramid==1.5.1',
    'pyramid_tm==0.7',
    'pyramid_debugtoolbar==2.2',
    'pyramid_beaker==0.8',
    'pytz',
    'twitter==1.14.3',
    'markdown==2.4.1',
    'decorator==3.4.0',
    'hurry.filesize==0.9',
    # 'pymysql3',
    'SQLAlchemy==0.9.7',
    'transaction==1.4.3',
    'repoze.tm2==2.0',  # default_commit_veto
    'zope.sqlalchemy==0.7.5',
    'waitress==0.8.9',
    'Babel==1.3',
    'mysql-connector-python==1.2.2'
]

setup_cmdclass = {}

try:
    import babel
    from setupcommands import ExtractMessagesJs, CompileCatalogJs
    from babel.messages.frontend import init_catalog as babel_init_catalog, update_catalog as babel_update_catalog
    setup_cmdclass = {
        'extract_messages_js': ExtractMessagesJs,
        'init_catalog_js': babel_init_catalog,
        'update_catalog_js': babel_update_catalog,
        'compile_catalog_js': CompileCatalogJs
    }
except ImportError:
    pass

# load version string
version_file = open(os.path.join('pyrone', 'version.py')).read()
mo = re.search("PYRONE_VERSION = '([0-9.]+)'", version_file)
if mo is None:
    print('No version found')
    sys.exit(1)

PYRONE_VERSION = mo.group(1)

setup(
    name='pyrone',
    version=PYRONE_VERSION,
    license='New BSD License',
    description='pyrone',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Framework :: Pyramid',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    author='Sergey Stolyarov',
    author_email='sergei@regolit.com',
    url='https://github.com/sigsergv/pyrone',
    data_files=[
        ('share/pyrone/examples', ['examples/'+x for x in ('development.ini', 'production.ini',
            'pyrone-blog-nginx-uwsgi.conf',
            'pyrone-blog-nginx-uwsgi-ssl.conf', 'pyrone-uwsgi.ini')]),
        ('share/pyrone', ['sample-data.json'])
    ],
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='pyrone',
    install_requires=requires,
    message_extractors={'pyrone': [
        ('**.py', 'python', {'encoding': 'utf-8'}),
        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'})
    ]},
    entry_points="""\
    [paste.app_factory]
    main = pyrone:main
    [console_scripts]
    pyronedbinit = pyrone.scripts.pyronedbinit:main
    """,
    cmdclass=setup_cmdclass
)
