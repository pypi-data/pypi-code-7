#!/usr/bin/env python

from distutils.core import setup

setup(name="gulpless",
      version="0.5",
      description="Simple python build system",
      author="Radu Dan",
      author_email="za_creature@yahoo.com",
      url="http://git.full-throttle.ro/radu/gulpless",
      packages=["gulpless"],
      install_requires=["watchdog", "termcolor", "pathtools"],
      entry_points={"console_scripts": ["gulpless=gulpless:main"]})
