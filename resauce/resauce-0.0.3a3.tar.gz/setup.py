from distutils.core import setup
from os import path
from pip.req import parse_requirements

requirements_location = path.join(path.dirname(__file__), "requirements.txt")
install_reqs = parse_requirements(requirements_location)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='resauce',
    author="Makerlabs",
    author_email="hello@makerlabs.co.uk",
    version='0.0.3a3',
    py_modules=['resauce'],
    install_requires=reqs,
)
