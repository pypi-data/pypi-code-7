from distutils.core import setup

setup(
    name='tube',
    version='0.1.4',
    author='Adam Gilman',
    author_email='me@adamgilman.com',
    packages=['tube'],
    scripts=[''],
    url='http://pypi.python.org/pypi/tube/',
    license='LICENSE',
    description='Python object wrapper for TfL (Transport for London) TrackerNet information service',
    install_requires=[
        "requests >= .5.0",
        "xmltodict >= 0.9.0",
    ],
)