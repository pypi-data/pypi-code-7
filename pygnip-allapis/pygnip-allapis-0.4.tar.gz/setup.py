from distutils.core import setup
setup(
  name = 'pygnip-allapis',
  packages = ['pygnip_allapis'],
  version = '0.4',
  description = 'A wrapper around the GNIP APIs',
  author = 'https://github.com/bee-keeper',
  author_email = 'none@none.com',
  url = 'https://github.com/bee-keeper/pygnip-allapis.git',
  download_url = 'https://github.com/bee-keeper/pygnip-allapis/tarball/0.1',
  keywords = ['gnip', 'api', 'wrapper'],
  classifiers = [],
  install_requires=[
    'requests>=2.4.1',
  ],
)