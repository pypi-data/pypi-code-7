import os

from setuptools import setup

setup(name='ConsistentHashing',
      version = '0.1.2',
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
      packages=['ConsistentHashing'],
      platforms=["Any"],
      license="BSD",
      keywords='hashing hash consistent distributed',
      description="A simple implement of consistent hashing.",
      long_description="A simple implement of consistent hashing."
)
