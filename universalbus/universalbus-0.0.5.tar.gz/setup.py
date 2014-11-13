from setuptools import setup


VERSION = "0.0.5"

setup(
    name='universalbus',
    description="Universal Bus over rabbitmq.",
    version=VERSION,
    url='https://github.com/KokocGroup/universal-bus',
    download_url='https://github.com/KokocGroup/universal-bus/tarball/v{}'.format(VERSION),
    packages=['universalbus'],
    install_requires=[
        'pika',
    ],
)
