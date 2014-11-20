import os
import sys
from setuptools import setup


if sys.argv[-1] == 'test':
    status = os.system('python tests/tests.py')
    sys.exit(1 if status > 127 else status)


requirements = [
    'centrifuge',
    'six>=1.3.0',
    'motor==0.3.4'
]


def long_description():
    return "MongoDB structure backend for Centrifuge"


setup(
    name='centrifuge-mongodb',
    version='0.3.0',
    description="MongoDB structure backend for Centrifuge",
    long_description=long_description(),
    url='https://github.com/centrifugal/centrifuge-mongodb',
    download_url='https://github.com/centrifugal/centrifuge-mongodb',
    author="Alexandr Emelin",
    author_email='frvzmb@gmail.com',
    license='MIT',
    packages=['centrifuge_mongodb'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Terminals',
        'Topic :: Text Processing',
        'Topic :: Utilities'
    ]
)
