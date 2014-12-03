from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='mycommute',
      version='0.101',
      description='Analyse my London commuting',
      url='http://github.com/ppuggioni/mycommute',
      author='Paolo Puggioni',
      author_email='p.paolo321@gmail.com',
      license='Apache2.0',
      packages=['mycommute'],
      install_requires=[
          'numpy',
          'pandas',
          'matplotlib',
          
      ],
      zip_safe=False)