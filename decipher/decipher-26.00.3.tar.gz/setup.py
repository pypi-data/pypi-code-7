from distutils.core import setup

setup(
    name='decipher',
    version='26.00.3',
    description="Package for easier access to Decipher's Beacon REST API",
    author='Erwin S. Andreasen',
    long_description=open('README.rst').read(),
    author_email='beacon-api@decipherinc.com',
    url='https://www.decipherinc.com/n/',
    packages=['decipher', 'decipher.commands'],
    license="BSD",
    requires=["requests"],
    scripts=['scripts/beacon']
)
