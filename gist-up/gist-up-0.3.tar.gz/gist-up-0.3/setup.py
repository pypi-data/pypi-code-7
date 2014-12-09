from distutils.core import setup

desc = ('A command line utility for publishing a directory and '
        'updating gists on your github account.')

setup(name='gist-up',
      version='0.3',
      description=desc,
      author='James R. Qualls',
      author_email='qualls.james@gmail.com',
      url='https://github.com/sourcec0de/gistup',
      download_url='https://github.com/sourcec0de/gistup/tarball/0.3',
      keywords=['gist', 'blogging', 'command line', 'github', 'publish'],
      scripts=['bin/gistup'],
      install_requires=[
          'PyGithub==1.25.2',
          'PyYAML==3.11',
          'argparse==1.2.2',
          'termcolor==1.1.0'
      ],
      classifiers=[])
