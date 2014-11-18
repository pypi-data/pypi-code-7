from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


def find_version(file_path):
    version_file = open(file_path).read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


app_name = 'cloud-resolve-conflicts'
script_name = 'cloud_resolve_conflicts.py'


os.remove(app_name)
os.symlink(os.path.join('cloud_resolve_conflicts', script_name), app_name)


setup(
    name=app_name,
    version=find_version(os.path.join('cloud_resolve_conflicts', script_name)),
    description="ownCloud and Seafile conflict resolver",
    long_description=long_description,
    url='https://bitbucket.org/rominf/cloud-resolve-conflicts',
    author='Roman Inflianskas',
    author_email='infroma@gmail.com',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cloud seafile owncloud remove conflict file duplicate',
    scripts=[app_name],
    install_requires=['send2trash', 'pathlib', 'flufl.enum'],
    packages=find_packages(exclude=['tests*']),
    package_data={
        'cloud_resolve_conflicts': ['package_data.dat'],
    },
)

