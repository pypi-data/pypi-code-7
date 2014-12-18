"""
Flask-MarcoPolo
"""

from setuptools import setup, find_packages
import flask_marcopolo

PACKAGE = flask_marcopolo

setup(
    name=PACKAGE.__NAME__,
    version=PACKAGE.__version__,
    license=PACKAGE.__license__,
    author=PACKAGE.__author__,
    author_email='mardix@github.com',
    description=PACKAGE.__doc__,
    long_description=PACKAGE.__doc__,
    url='http://mardix.github.io/flask-marcopolo/',
    download_url='http://github.com/mardix/flask-marcopolo/tarball/master',
    py_modules=['flask_marcopolo'],
    entry_points=dict(console_scripts=['flask-marcopolo=flask_marcopolo.cmd:main']),
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Flask==0.10.1',
        'Flask-Classy==0.6.10',
        'Flask-Assets==0.10',
        'Flask-Mail==0.9.1',
        'Flask-WTF==0.9.5'
    ],

    keywords=['flask', 'templates', 'views', 'classy', 'marcopolo', 'framework'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
