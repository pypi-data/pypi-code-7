import os, time, compileall
from setuptools import setup, find_packages

path = os.path.abspath(os.path.dirname(__file__))+"\\django_microsip_base\\"
compileall.compile_dir(path, force=True)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
# this grabs the requirements from requirements.txt
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
# setup(
#     install_requires=REQUIREMENTS
# )


# from ez_setup import use_setuptools
# use_setuptools()


setup(
  name = 'django-microsip-base',
  version ='0.0.7',
  packages = find_packages(),
  include_package_data = True,
  description = "Django Microsip Base",
  long_description = README,
  author = "Servicios de Ingenieria Computacional",
  author_email = "jesusmaherrera@gmail.com",
  classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
  install_requires=REQUIREMENTS,
)