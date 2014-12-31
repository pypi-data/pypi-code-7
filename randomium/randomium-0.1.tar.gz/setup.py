from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
  name='randomium',
  version='0.1',
  description='Tools for generating random things.',
  long_description=readme(),
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Testing',
  ],
  url='http://github.com/jachin/randomium',
  author='Jachin Rupe',
  author_email='jachin@jachin.rupe.name',
  license='MIT',
  packages=['randomium'],
  zip_safe=False,
  entry_points = {
        'console_scripts': ['random-animal=randomium.command_line:main'],
    }
)
