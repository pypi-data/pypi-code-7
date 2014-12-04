import os

from setuptools import setup

fd = open('./README')
long_desc = fd.read()
fd.close()

setup(name='ConsistentHashing',
      version = '0.2.0',
      author="Ziang Guo",
      author_email="iziang@yeah.net",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      py_modules=['consistenthashing'],
      platforms=["Any"],
      license="BSD",
      keywords='hashing hash consistent distributed',
      description="A simple implement of consistent hashing.",
      long_description=long_desc
)
