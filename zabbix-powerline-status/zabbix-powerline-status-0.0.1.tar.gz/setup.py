from setuptools import setup, find_packages

setup(
    name='zabbix-powerline-status',
    author='Colin Wood',
    author_email='cwood06@gmail.com',
    url='http://bitbucket.org/colinbits/zabbix-powerline-status',
    download_url='http://bitbucket.org/colinbits/zabbix-powerline-status',
    long_description='A extension to powerline to show zabbix triggers',
    version='0.0.1',
    include_package_data=True,
    install_requires=[
        'zabbix-client==0.1.0'
    ],
    packages=find_packages(),
    description='Zabbix powerline extension to show current triggers',
    tests_require=[
        'nose',
    ],
    keywords=[],
)
