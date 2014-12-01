try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='cuecloud',
      version='1.0.3',
      description='Integration library for CueCloud',
      author='Cuecloud',
      author_email='info@cuecloud.com',
      url='https://github.com/cuecloud/cuecloud-py',
      license="MIT License",
      install_requires=['requests>=1.0'],
      tests_require=['mock', 'nose'],
      packages=['cuecloud'],
      platforms='any',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ]
     )

