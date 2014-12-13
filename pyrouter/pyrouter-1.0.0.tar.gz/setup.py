import os
from setuptools import setup, find_packages


requirements_file = open('%s/requirements.txt' % os.path.dirname(os.path.realpath(__file__)), 'r')
install_requires = [line.rstrip() for line in requirements_file]
base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="pyrouter",
    version="1.0.0",
    description="Associate a request with the code that will convert it to a response",
    long_description="\n\n".join([
        open(os.path.join(base_dir, "README.rst"), "r").read(),
    ]),
    url="https://github.com/felixcarmona/pyrouter",
    author="Felix Carmona",
    author_email="mail@felixcarmona.com",
    packages=find_packages(exclude=('pyrouter.tests', 'pyrouter.tests.*')),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="pyrouter.tests.get_tests",
)