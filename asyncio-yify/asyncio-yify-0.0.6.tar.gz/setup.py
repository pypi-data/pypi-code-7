from setuptools import setup

setup(
    name='asyncio-yify',
    version='0.0.6',
    author='davidyen1124',
    author_email='davidyen1124@gmail.com',
    description='Damned fast YIFY parser using Asyncio',
    lincense='Apache',
    keywords='yify parser movies asyncio',
    url='https://github.com/davidyen1124/Asyncio-YIFY',
    packages=['yify'],
    install_requires=[
        'requests==2.5.0',
        'aiohttp==0.11.0',
        'lxml==3.4.1',
    ],
)
