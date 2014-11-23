
from setuptools import setup

VERSION = '0.1.0a1'

setup(
    name="taskpromises",
    version=VERSION,
    author="Emlyn O'Regan / Training Evidence Systems Pty Ltd",
    author_email='emlyn@tesapp.com',
    maintainer="Emlyn O'Regan / Training Evidence Systems Pty Ltd",
    maintainer_email='emlyn@tesapp.com',
    description="An distributed implementation of Promises for Google Appengine Tasks",
    url='...',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    packages=['taskpromises'],
    install_requires=[
    ],
    keywords='promises tasks appengine gae'
)
