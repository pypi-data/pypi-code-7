from setuptools import setup
import nanodb_driver

setup(
    name='nanodb_driver',
    version=nanodb_driver.__version__,
    author='Pierre-Marie Dartus',
    author_email='dartus.pierremarie@gmail.com',
    packages=['nanodb_driver'],
    license='LICENSE.txt',
    url='https://github.com/nano-db/nanodb_driver',
    description='Driver to interface application with a NanoDB server',
    long_description=open('README.rst').read(),
    install_requires=[
        "pyzmq>=14.4.1"
    ],
)
