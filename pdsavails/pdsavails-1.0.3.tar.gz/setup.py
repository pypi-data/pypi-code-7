try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pdsavails',
      version='1.0.3',
      description='Integration library for PDSAvails',
      author='David Litwin',
      author_email='david@premieredigital.net',
      url='https://github.com/premieredigital/PDSAvails/',
      license="MIT License",
      install_requires=['requests>=1.0'],
      tests_require=['mock', 'nose'],
      packages=['pdsavails'],
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

