import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
import os

name = "verify_version_spec"
version = "0.0.2"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    author='Jake Hickenlooper',
    author_email='jake@weboftomorrow.com',
    description="Verify that a version specification matches a version string.",
    long_description=read('README.md'),
    url='https://github.com/jkenlooper/verify_version_spec',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
        ],
    py_modules=['verify_version_spec'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'semantic_version',
        'docopt',
      ],
    entry_points={
        'console_scripts': [
            'verify_version_spec = verify_version_spec:main',
            ]
        },
)
