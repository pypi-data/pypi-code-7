from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='wicomm',
      version='0.12',
      description='Python package containing a wireless communication API to be used in robotics applications.',
      long_description='Provides a framework to receive data over a socket and pump it into a shared memory.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='wicomm',
      url='http://hardworkin-man.com:8080/scm/git/wicomm',
      author='Mike Moore',
      author_email='mickety.mike@gmail.com',
      license='MIT',
      packages=['wicomm'],
      install_requires=[
          #'markdown',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/ReadFromSharedMem','bin/WriteToSharedMem'],
      include_package_data=True,
      zip_safe=False)