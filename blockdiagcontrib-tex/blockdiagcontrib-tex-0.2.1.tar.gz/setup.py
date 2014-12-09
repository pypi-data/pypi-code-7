from setuptools import setup


__version__ = '0.2.1'
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

setup(
    name='blockdiagcontrib-tex',
    version=__version__,
    description='TeX plugin for blockdiag',
    long_description=open('readme.markdown').read(),
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author="Yassu 0320",
    author_email='mathyassu at gmail.com',
    url='http://bitbucket.org/blockdiag/blockdiag-contrib',
    license='Apache License 2.0',
    packages=['blockdiagcontrib'],
    include_package_data=True,
    entry_points="""
        [blockdiag_plugins]
        tex=blockdiagcontrib.tex
    """
)
