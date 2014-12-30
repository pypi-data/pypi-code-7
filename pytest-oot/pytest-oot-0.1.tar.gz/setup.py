
from setuptools import setup

setup(
    name='pytest-oot',
    description='Run object-oriented tests in a simple format',
    author='Steven LI',
    author_email='steven004@gmail.com',
    version='0.1',
    py_modules = ['pytest_oot'],
    entry_points = {
        'pytest11': [
            'pytest_oot = pytest_oot',
        ]
    },
    install_requires = ['py>=1.3.0', 'pytest'],
)
