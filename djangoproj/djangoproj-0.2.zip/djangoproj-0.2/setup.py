from setuptools import setup, find_packages
setup(
	name = "djangoproj",
	version = "0.2",
	packages = find_packages(),
	author = "Anon",
        install_requires = ['Django==1.6.5','django-bootstrap-toolkit==2.15.0'],
	include_package_data = True
	)
