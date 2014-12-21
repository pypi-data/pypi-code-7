from distutils.core import setup
from distutils.extension import Extension

module1 = Extension(
    '_gost89', 
    sources= [
        'ext/gost89.c', 'ext/gosthash.c', 'ext/sbox.c', 
        'ext/_gost89.c',
    ],
)

setup(
    name = 'gost89',
    version = '0.0.1',
    description = 'Gost89 bindings for python',
    url='https://github.com/dstucrypt/python-gost89',
    author='Ilya Petrov',
    author_email='ilya.muromec@gmail.com',
    ext_modules = [module1],
    packages=[
        'gost89',
    ],
)
