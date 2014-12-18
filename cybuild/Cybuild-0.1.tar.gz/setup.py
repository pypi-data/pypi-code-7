from distutils.core import setup

import version

with open('README.md', 'rb') as README:
    description = README.read()

setup(name='Cybuild',
      version=version.getVersion(),
      description=description,
      keywords='Cython inline extension build scipy',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/cfobel/Cybuild',
      license='GPL',
      packages=['Cybuild'],
      install_requires=['path_helpers', 'functools32', 'Cython', 'numpy',
                        'scipy'])
