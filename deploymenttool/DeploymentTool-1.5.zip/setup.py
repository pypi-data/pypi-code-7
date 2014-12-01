from setuptools import setup
setup(
	name = "DeploymentTool",
	version = "1.5",
	packages = ['Deployment'],
	author = "Muhammad Irfan & Reza Adiyat",
	author_email = "muhammad.irfan92@gmail.com & rezaadiyat@gmail.com",
    license = "BSD",
	platform = "Python",
	install_requires = [
		"pip ==1.5.6",
		"Django ==0.6.5",
		"django-bootstrap-toolkit ==2.15.0",
		"esdsa ==0.11",
		"Fabric ==1.9.0",
		"MySQL-Connector-Python ==2.0.1",
		"MySQL-python ==1.2.3",
		"paramiko ==1.14.0",
		"pycripto ==2.1.0",
		"setuptools ==7.0",
		],
	classifiers=[
		"Environment :: Web Environment",
		"Framework :: Django",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
	],
	include_package_data = True,
    description = "Our deployment tool using django and fabric"
	)
