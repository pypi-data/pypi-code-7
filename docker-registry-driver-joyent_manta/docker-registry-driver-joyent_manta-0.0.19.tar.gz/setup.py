from distutils.core import setup

setup(
    name='docker-registry-driver-joyent_manta',
    version='0.0.19',
    author='Vladimir Bulyga',
    author_email='xx@ccxx.cc',
    packages=['docker_registry', 'docker_registry.drivers'],

    scripts=[],
    url='https://github.com/13W/docker-registry-driver-manta.git',
    license='LICENSE.txt',
    description='Docker registry manta driver',
    long_description=open('README.md').read(),
    install_requires=open('./requirements.txt').read()
)
