from setuptools import setup

setup(name='fcs_simulation',
      version='0.1.1e',
      author='Tyler Parker',
      description='Simulate FCS and generate photon arrival times',
      url='http://github.com/computemachines/fcs_simulation',
      author_email='tparker@umass.edu',
      license='MIT',
      packages=['fcs_simulation'],
      dependency_links=['https://github.com/bgamari/photon-tools/tarball/master#egg=photon-tools-1.0'],
      install_requires=['photon_tools'],
      zip_safe=False)
