from setuptools import setup

setup(name="wrapPydas",
        version="0.1.2",
        author="Brian Chapman",
        author_email="brian.chapman@utah.edu",
        package_dir={'wrapPydas':'src'},
        url="https://github.com/chapmanbe/wrapPydas",
        install_requires=["pydas"],
        packages=['wrapPydas'],
    )
