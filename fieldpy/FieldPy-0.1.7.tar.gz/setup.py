from distutils.core import setup

setup(
    name='FieldPy',
    version='0.1.7',
    author='Adamos Kyriakou',
    author_email='somada141@gmail.com',
    packages=['fieldpy',
              'fieldpy.test',
              'fieldpy.primitives',
              'fieldpy.interpolation',
              'fieldpy.analysis'],
    package_data={'fieldpy.test': ['data/*.*']},
    url='http://pypi.python.org/pypi/FieldPy/',
    license='LICENSE.txt',
    description='A collection of primitives and tools relating to the analysis and manipulation of 2D and 3D fields',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.8.0",
        "pandas >= 0.14.0",
        "scipy >= 0.14.0",
        "h5py >= 2.2.1",
        "nose >= 1.3.3",
    ],
)
