# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'hatak>=0.2.3',
    'toster',
    'hatak_sql',
    'formskit>=0.5.0',
]

if __name__ == '__main__':
    setup(
        name='Hatak_Toster',
        version='0.2.1',
        description='Toster plugin for Hatak.',
        license='Apache License 2.0',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        namespace_packages=['haplugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
    )
