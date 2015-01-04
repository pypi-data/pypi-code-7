import os
from distutils import log # needed for outputting information messages 
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts

class OverrideInstall(install):

    def run(self):
        install.run(self)
        dir_to_handle = set()
        mode = 0777
        for filepath in self.get_outputs():
          dir_to_handle.add(os.path.dirname(filepath))
        for d in dir_to_handle:
          log.info("%s -> %s" % (d, oct(mode)))
          os.chmod(d, mode)

files = \
[
  t.replace('goenv/', '') for t in reduce(
    lambda a, b: a+b, [
      map(lambda y: x[0]+'/'+y, x[2]) \
      for x in os.walk('goenv/data')
    ]
  )
] + [
  'goenv.sh'
]


setup(
  name='goenv',
  version='0.0.8',
  description='Golang environment manager',
  url='https://github.com/biinilya/goenv',
  author='Ilya Biin',
  author_email='me@ilyabiin.com',
  packages=['goenv'],
  scripts=['goenv/goenv'],
  package_data={'goenv': files},
  cmdclass={'install': OverrideInstall},
)
