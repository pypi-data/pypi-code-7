from setuptools import find_packages, setup
import virtualenvapi

version = virtualenvapi.__version__

setup(
    name='ar-virtualenv-api',
    version=version,
    license='BSD',
    author='arteria GmbH',
    author_email='admin@arteria.ch',
    description='An API for virtualenv/pip',
    url='https://github.com/arteria/ar-virtualenv-api',
    packages=find_packages(),
)
