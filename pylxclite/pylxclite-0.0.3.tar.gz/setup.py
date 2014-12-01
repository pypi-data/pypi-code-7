from setuptools import setup, find_packages

version = '0.0.3'

setup(name='pylxclite',
      description="A python wrapper for Linux Containers (LXC)",
      long_description="A python wrapper for LXC commands",
      version=version,
      url='https://github.com/Unixlike/pylxclite',
      author="Camel",
      author_email="393789775@qq.com",
      packages=find_packages(),
      zip_safe=True,
      license = "LGPLv3",
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: System Administrators',
                     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python :: 2.6',
                     'Topic :: System :: Systems Administration'],
      
      )
