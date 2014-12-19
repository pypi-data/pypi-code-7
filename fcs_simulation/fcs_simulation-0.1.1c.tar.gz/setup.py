from setuptools import setup

setup(name='fcs_simulation',
      version='0.1.1c',
      author='Tyler Parker',
      description='Simulate FCS and generate photon arrival times',
      url='http://github.com/computemachines/fcs_simulation',
      author_email='tparker@umass.edu',
      license='MIT',
      packages=['fcs_simulation'],
      install_requires=['photon_tools'],
      dependency_links=['https://github.com/bgamari/photon-tools/tarball/master#egg=photon-tools-1.0'],
      zip_safe=False)
