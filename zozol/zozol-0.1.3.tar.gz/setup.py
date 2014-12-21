# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="zozol",
    version='0.1.3',
    url='https://github.com/muromec/zozol',
    description='',
    author='Ilya Petrov',
    author_email='ilya.muromec@gmail.com',
    packages=["zozol"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[ ],
    tests_require=[
        'gost89',
        'nose',
    ],
    setup_requires=['nose>=1.0'],
    classifiers=[
        'Programming Language :: Python',
    ]
)
