from setuptools import setup

setup(name='PyDictionary',
      version='1.0',
      description='Python Module to get meaning of words and to translate them',
      author='Pradipta Bora',
      author_email='pradd@outlook.com',
      license='MIT',
      packages=['PyDictionary'],
      install_requires=[
            'beautifulsoup4','goslate','requests',],
      zip_safe=False)
