from setuptools import setup

setup(name='osf',
      version='1.9',
      description='OSF in python',
      author='luto',
      author_email='m@luto.at',
      license='AGPLv3',
      url='https://github.com/luto/osf.py',
      packages=['osf'],
      install_requires=[
          'modgrammar'
      ],
     )
