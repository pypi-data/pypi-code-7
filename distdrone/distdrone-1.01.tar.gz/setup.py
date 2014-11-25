from setuptools import setup

def readme():
	with open("README.txt") as f:
		return f.read()

setup(name="distdrone",
	version="1.01",
	description="package to drive parallel drone swarm",
	url="http://github.com/isaacrob/paradrone",
	author="Isaac Robinson",
	author_email="isaacrob@me.com",
	license="MIT",
	packages=["distdrone","distdrone.motion"],
	scripts=["bin/trigger","bin/testpredictor","bin/centersearch","bin/installdronedeps"],
	platform=['Raspberry Pi with Raspbian'],
	zip_safe=False)