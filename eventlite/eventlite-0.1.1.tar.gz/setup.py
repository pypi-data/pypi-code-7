import os
from setuptools import setup, find_packages

version = '0.1.1'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
    longdesc += "\n\n" + fp.read()


setup(
    name='eventlite',
    version=version,
    packages=find_packages(),
    url='PACKAGE_URL',
    license='BSD License',
    author='Samuele Santi',
    author_email='',
    description='',
    long_description=longdesc,
    install_requires=[],
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: BSD License',

        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
