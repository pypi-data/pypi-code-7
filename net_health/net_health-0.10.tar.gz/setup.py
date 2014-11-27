from setuptools import setup

setup(name='net_health',
      version='0.10',
      description='check network connectivity',
      url='',
      author='Gilad Zohari',
      author_email='gzohari@gmail.com',
      scripts=['bin/check_connectivity'],
      license='MIT',
      install_requires=[
          'python-neutronclient', 'python-novaclient'
      ],
      packages=['net_health'],
      entry_points={
          'ceilometer.poll.compute': [
              'latency_pollster=ceilometer.compute.pollsters.latency_pollster:LatencyPollster',
          ],
      },
      zip_safe=False)
