from setuptools import setup
import os


def get_version(path):
    fn = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        path, "__init__.py")
    with open(fn) as f:
        for line in f:
            if '__version__' in line:
                parts = line.split("=")
                return parts[1].split("'")[1]


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGELOG = open(os.path.join(here, 'CHANGELOG.rst')).read()


setup(
    name="devpi-ldap",
    description="devpi-ldap: LDAP authentication for devpi-server",
    long_description=README + "\n\n" + CHANGELOG,
    url="https://github.com/devpi/devpi-ldap",
    version=get_version("devpi_ldap"),
    maintainer="Florian Schulze",
    maintainer_email="florian.schulze@gmx.net",
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"] + [
            "Programming Language :: Python :: %s" % x
            for x in "2 3 2.7 3.4".split()],
    entry_points={
        'console_scripts': [
            "devpi-ldap = devpi_ldap.main:main"],
        'devpi_server': [
            "devpi-ldap = devpi_ldap.main"]},
    install_requires=[
        'PyYAML',
        'devpi-server>=2.0.0',
        'python3-ldap'],
    include_package_data=True,
    zip_safe=False,
    packages=['devpi_ldap'])
