try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

with open('readme.rst') as reader:
    long_description = reader.read()
    
setup(name='theape',
      long_description=long_description,
      version= '2014.11.10',
      description="The All-Purpose Experimenter.",
      author="russell",
      platforms=['linux'],
      url = '',
      author_email="necromuralist@gmail.com",
      license = "",
      install_requires = ['pudb', 'paramiko', 'numpy', 'docopt'],
      packages = find_packages(),
      include_package_data = True,
      package_data = {"ape":["*.txt", "*.rst", "*.ini"]},
      entry_points = """
	  [console_scripts]
      ape=ape.main:main

      [ape.subcommands]
      subcommands=ape.infrastructure.arguments

      [ape.plugins]
      plugins = ape.plugins
      """
      )

# an example last line would be cpm= cpm.main: main

# If you want to require other packages add (to setup parameters):
# install_requires = [<package>],
#version=datetime.today().strftime("%Y.%m.%d"),
# if you have an egg somewhere other than PyPi that needs to be installed as a dependency, point to a page where you can download it:
# dependency_links = ["http://<url>"]
