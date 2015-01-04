"""Workaround a bug in setuptools that prevents you from listing the same
package as both a setup_requires and an install_requires"""

from setuptools import setup

setup(
    name="headers_workaround",
    packages=["headers_workaround"],
    version="0.1",
    author="Matthew Honnibal",
    author_email="honnibal@gmail.com",
    url="http://github.com/syllog1sm/headers_workaround",
    package_data={"": ["*.h", "numpy/*.h"]},
    description="""Add this to setup_requires, and use it to fetch headers.""",
    classifiers=[
                'Environment :: Console',
                'Operating System :: OS Independent',
                'Intended Audience :: Science/Research',
                'Programming Language :: Cython',
                'Topic :: Scientific/Engineering'],
)


