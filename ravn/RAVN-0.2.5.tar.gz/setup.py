from distutils.core import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'tests/runtests.py'])
        raise SystemExit(errno)

setup(
  name = 'RAVN',
  packages = ['RAVN'], # this must be the same as the name above
  version = '0.2.5',
  description = 'Next Gen Smart Drone Platform',
  author = 'RaptorBird Robotics Inc.',
  author_email = 'contact@raptorbird.com',
  url = 'https://github.com/raptorbird/RAVN', # use the URL to the github repo
  download_url = 'https://github.com/raptorbird/RAVN/tarball/0.1', # I'll explain this in a second
  keywords = ['ravn', 'drone', 'development', 'smart'], # arbitrary keywords
  classifiers = [],
  install_requires = ['ws4py', 'droneapi']
)