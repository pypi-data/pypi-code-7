from distutils.core import setup

setup(
    name='EulerMods',
    version='0.1.2',
    author='Ryan Cox',
    author_email='arconyx6@gmail.com',
    url='https://pypi.python.org/pypi/EulerMods/',
    packages=['mods'],
    license='LICENSE.txt',
    description='Modules to aid in Project Euler calculations though functions for common tasks.',
    long_description=open('README.txt').read(),
    classifiers=[
        'Programming Language :: Python :: 3.4'
        ],
)
