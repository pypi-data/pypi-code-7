from distutils.core import setup

setup(name='cbuh',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Tom\'s contact list',
      url='https://github.com/tlevine/cbuh',
      packages=['cbuh'],
#     install_requires = [
#         'xapian>=1.2.18',
#     ],
      scripts = [
          'bin/cbuh',
      ],
      version='0.0.1',
      license='AGPL',
      classifiers=[
          'Programming Language :: Python :: 2.7',
      ],
)
