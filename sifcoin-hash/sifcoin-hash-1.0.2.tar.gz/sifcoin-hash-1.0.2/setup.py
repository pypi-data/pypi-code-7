from distutils.core import setup, Extension
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

sifcoin_hash_module = Extension('sifcoin_hash',
                               sources = ['sifcoinmodule.c',
                                          'sifcoin.c',
                                          'sha3/blake.c',
                                          'sha3/bmw.c',
                                          'sha3/groestl.c',
                                          'sha3/jh.c',
                                          'sha3/keccak.c',
                                          'sha3/skein.c'],
                               include_dirs=['./sifcoin-hash', './sha3', './'])

setup(
    name='sifcoin-hash',
    version='1.0.2',
    description = 'Bindings for Proof of Work hash function used by SiFcoin',
    long_description=long_description,
    url='https://github.com/gjhiggins/sifcoin-hash',
    author='Graham Higgins',
    author_email='gjh@bel-epa.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cryptocurrency',
    ext_modules=[sifcoin_hash_module]
)
