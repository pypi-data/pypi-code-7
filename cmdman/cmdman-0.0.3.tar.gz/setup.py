import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(
    # General information.
    name='cmdman',
    description='Simple command line program wrapper adding debugging arguments.',

    url='https://github.com/fmichea/cmdman',

    # Version information.
    license='BSD',
    version='0.0.3',

    # Author information.
    author='Franck Michea',
    author_email='franck.michea@gmail.com',

    # File information.
    packages=find_packages(exclude=['tests', 'examples']),

    # PyPI categories.
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
    ],
)
