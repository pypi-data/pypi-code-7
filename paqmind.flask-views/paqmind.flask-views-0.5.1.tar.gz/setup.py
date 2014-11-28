from setuptools import setup, find_packages

setup(
    name = 'paqmind.flask-views',
    description = 'Class-based views for Flask',
    version = '0.5.1',
    license = 'MIT',
    install_requires = ['pytz', 'flask', 'paqmind.flask-routes>=0.2.1', 'paqroles>=1.0.0'],
    packages = find_packages(),
    include_package_data = True,
)
