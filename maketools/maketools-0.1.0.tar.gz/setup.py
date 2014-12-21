import os
from setuptools import setup

readme_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'README.md',
)
long_description = open(readme_path).read()

setup(
  name='maketools',
  version='0.1.0',
  packages=['maketools'],
  author="Nick Whyte",
  author_email='nick@nickwhyte.com',
  description="Add build prerequisites to your python project.",
  long_description=long_description,
  url='https://github.com/nickw444/python-maketools',
  include_package_data=True,
  zip_safe=False,
  install_requires=[
    "Flask",
  ],
)
