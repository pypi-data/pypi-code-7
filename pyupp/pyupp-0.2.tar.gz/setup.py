from setuptools import setup

version = '0.2'

setup(
    name='pyupp',
    version=version,
    description="Read and write unity player preferences data.",
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='unity',
    author='Peter Ruibal',
    author_email='ruibalp@gmail.com',
    url='https://github.com/fmoo/pyupp',
    license='Apache',
    py_modules=[
        'pyupp',
    ],
    requires=[
        'six',
    ],
)
