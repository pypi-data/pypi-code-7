from setuptools import setup

setup(name='fcs_simulation',
      version='0.1.1b',
      author='Tyler Parker',
      description='Simulate FCS and generate photon arrival times',
      url='http://github.com/computemachines/fcs_simulation',
      author_email='tparker@umass.edu',
      license='MIT',
      packages=['fcs_simulation'],
      dependency_links=['https://github.com/bgamari/photon-tools.git'],
      zip_safe=False)
