from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = "0.3.1"

long_description = ""
try:
    long_description=file('README.md').read()
except Exception:
    pass

license = ""
try:
    license=file('LICENSE').read()
except Exception:
    pass




setup(
    name='pyncomings',
    version=version,
    author_email='saavedra.pablo@interoud.com',
    author='Pablo Saavedra Rodinho',
    description='Log entries parser',
    url='https://tracker.interoud.com/sistemas/',
    install_requires=[],
    packages=[
        'pyncomings',
        'pyncomings.dao',
        'pyncomings.parsers'
    ],
    scripts=[
        'tools/pyncomings',
        'tools/pyncomings-sanitizer',
        'tools/pyncomings-garbage-collector',
    ],
    data_files=[
        ('share/doc/pyncomings', ['doc/pyncomings.conf',
                ])
    ],


    # download_url= 'https://github.com/psaavedra/chic/zipball/master',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=long_description,
    license=license,
    keywords = "python parser log",

)

