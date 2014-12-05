from setuptools import setup

setup(
    name="nlgserv",
    version="0.2.2",
    author="Darren Richardson",
    packages=["nlgserv","nlgserv.tests"],
    package_data={"nlgserv":["simplenlg.jar","jython.jar"]},
    scripts=["bin/nlgserv"],
    license="LICENSE.txt",
    description="JSON HTTP wrapper for SimpleNLG",
    long_description=open("README.md").read()
)
