import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-selenium-boilerplate',
    version='0.0.5',
    packages=['selenium_boilerplate'],
    install_requires=['selenium'],
    include_package_data=True,
    license='BSD License',
    description='Boilerplate for setting up selenium tests in Django',
    long_description=README,
    url="https://github.com/yourcelf/django-selenium-boilerplate.git",
    author="Charlie DeTar",
    author_email="cfd@media.mit.edu",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)
