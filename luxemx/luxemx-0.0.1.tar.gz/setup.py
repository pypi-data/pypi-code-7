from setuptools import setup

setup(
    name = 'luxemx',
    version = '0.0.1',
    author = 'Rendaw',
    author_email = 'spoo@zarbosoft.com',
    packages = ['luxemx'],
    url = 'https://github.com/Rendaw/luxemx',
    download_url = 'https://github.com/Rendaw/luxemx/tarball/v0.0.1',
    license = 'BSD',
    description = 'Extracts specified elements from luxem documents',
    long_description = open('readme.txt', 'r').read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Text Processing :: Filters',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires = ['luxem'],
    entry_points = {
        'console_scripts': [
            'luxemx = luxemx.luxemx:main',
        ],
    }
)
