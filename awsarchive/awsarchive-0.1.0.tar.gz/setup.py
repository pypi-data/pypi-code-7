from setuptools import setup, find_packages


VERSION = '0.1.0'


setup(
    name='awsarchive',
    version=VERSION,
    author='Billy Shambrook',
    author_email='billy.shambrook@gmail.com',
    description='Toolkit for archiving files using AWS products.',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords="aws glacier s3 backup archive sqs",
    packages=find_packages(exclude='docs'),
    url="https://github.com/billyshambrook/awsarchive",
    download_url="https://github.com/billyshambrook/awsarchive/tarball/{}".format(VERSION),
    install_requires=['boto'],
    entry_points={
        'console_scripts': [
            'awsarchive = awsarchive.__init__:main'
        ]
    }
)
