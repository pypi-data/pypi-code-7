from setuptools import setup

from systempay import __version__


setup(
    name='systempay',
    version=__version__,
    description="Systempay API Client",
    author="Jurismarchés",
    author_email='contact@jurismarches.com',
    url='',
    packages=[
        'systempay',
        'systempay.codes'
    ],
    install_requires=[
        'pytz==2014.7',
        'python-dateutil==2.2',
        'suds-jurko==0.6'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ])
