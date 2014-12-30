from setuptools import setup
import south_mysqlndb

setup(
    name='south_mysqlndb',
    version=south_mysqlndb.__version__,
    description='south database adapter for mysqlndb',
    url='https://github.com/jimmykobe1171/south-mysqlndb',
    author='Jimmy Cheung',
    author_email='jimmykobe1171@126.com',
    license='MIT',
    packages=['south_mysqlndb'],
    zip_safe=False
    )
