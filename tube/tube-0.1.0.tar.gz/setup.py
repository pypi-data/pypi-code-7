from distutils.core import setup

setup(
    name='tube',
    version='0.1.0',
    author='Adam Gilman',
    author_email='me@adamgilman.com',
    packages=['tube', 'tube'],
    scripts=[''],
    url='http://pypi.python.org/pypi/tube/',
    license='LICENSE.txt',
    description='Python object wrapper for TfL (Transport for London) TrackerNet information service',
    long_description=open('README.md').read(),
    install_requires=[
        "requests==2.5.0",
        "xmltodict==0.9.0",
    ],
)