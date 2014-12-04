from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()

setup(
    name='fptest',
    version='0.0.3',
    description='A TIBCO Fulfilment Provisioning test helper',
    # long_description=long_description,
    packages=['fptest'],
    url='https://github.com/oxo42/FpTest',
    author='John Oxley',
    author_email='john.oxley@gmail.com',
    license='Apache',

    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    requires=['lxml', 'requests']
)
