import os
import re
from setuptools import setup

with open(
    os.path.join(os.path.dirname(__file__), 'correcthorsebatterystaple', '__init__.py')
) as app_file:
    version = re.compile(
        r".*__version__ = '(.*?)'", re.S
    ).match(app_file.read()).group(1)

with open("README.md") as readme:
    long_description = readme.read()


setup(
    name="correcthorsebatterystaple",
    version=version,
    author="Teemu Kokkonen",
    author_email="teemu.on.ihminen@gmail.com",
    description=("Test application"),
    license="BSD",
    keywords="example documentation tutorial",
    url="https://github.com/Frozenball/correcthorsebatterystaple",
    packages=['correcthorsebatterystaple'],
    entry_points={
        'console_scripts': ['correcthorsebatterystaple=correcthorsebatterystaple.app:main'],
    },
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        'click==3.3'
    ]
)
