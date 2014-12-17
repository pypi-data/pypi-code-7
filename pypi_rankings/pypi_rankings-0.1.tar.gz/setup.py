
SETUP_INFO = dict(
    name = 'pypi_rankings',
    version = '0.1',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/wiggin15/pypi_rankings',
    license = 'PSF',
    description = """show PyPI rankings""",
    long_description = """collect and display information and ranking of all projects in PyPI""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['setuptools', 'requests', 'infi.execute', 'infi.pypi_manager', 'itertools_recipes', 'Flask'],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['start_pypi_rankings = pypi_rankings.webserver:main'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

