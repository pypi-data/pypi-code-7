from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()
        
setup(name='pytidyclub',
      version='0.0.2',
      description='A simple Python wrapper for the TidyClub API',
      long_description=readme(),
      url='http://github.com/kyerussell/pytidyclub',
      author='Kye Russell',
      author_email='me@kye.id.au',
      license='MIT',
      packages=['pytidyclub'],
      zip_safe=False)
