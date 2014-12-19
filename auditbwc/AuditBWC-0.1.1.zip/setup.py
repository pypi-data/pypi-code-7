import os
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# pip install -e .[develop]
develop_requires = [
    'WebTest',
    'PyQuery',
]

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()
VERSION = open(os.path.join(cdir, 'auditbwc', 'version.txt')).read().strip()

setup(
    name='AuditBWC',
    version=VERSION,
    description="A record history and comparison component for the BlazeWeb framework",
    long_description='\n\n'.join((README, CHANGELOG)),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
    ],
    author='Randy Syring',
    author_email='rsyring@gmail.com',
    url='http://bitbucket.org/blazelibs/auditbwc/',
    license='BSD',
    packages=['auditbwc'],
    include_package_data=True,
    zip_safe=False,
    extras_require={'develop': develop_requires},
    install_requires=[
        'SQLAlchemyBWC',
        'WebGrid',
        'BlazeWeb',
    ],
)
