from setuptools import setup

setup(
    name='aiqpy',
    version='0.2',
    description='Python bindings for connecting to a AIQ8 server',
    author='Erik Lundberg',
    author_email='lundbergerik@gmail.com',
    packages=['aiqpy'],
    install_requires=[
        'requests',
        'six'
    ],
    keywords=['aiq8', 'appear', 'rest', 'api'],
    zip_safe=False
)
