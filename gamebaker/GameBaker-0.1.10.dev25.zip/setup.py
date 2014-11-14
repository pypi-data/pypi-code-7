from distutils.core import setup
from os.path import join

setup(
    name="GameBaker",
    version="0.1.10.dev25",
    description="High level framework for making games and simulations based on Pygame",
    url="https://pypi.python.org/pypi/GameBaker",
    packages=["gamebaker",],
    data_files=[("scripts", [join("bin", "red_square.png")])],
    author="Roderick MacSween",
    author_email="macsweenroddy@gmail.com",
    license="MIT",
    long_description=open("README.txt").read(),
    scripts=[join("bin", "gamebakerscripts.py"),],
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: Implementation :: CPython",
                 "Topic :: Games/Entertainment",
                 "Topic :: Multimedia",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Software Development :: Libraries :: pygame",
                 "License :: OSI Approved :: MIT License",],
)