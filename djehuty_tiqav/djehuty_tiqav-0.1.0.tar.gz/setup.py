import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

install_requires = [
    'djehuty>=0.0.5',
    'requests>=2.3.0',
]

setup(name='djehuty_tiqav',
      version='0.1.0',
      description='djehuty_tiqav',
      long_description=README,
      author='xica development team',
      author_email='info@xica.net',
      url='https://github.com/xica/djehuty-tiqav',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Pyramid',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Communications :: Chat',
      ],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=install_requires,
      test_suite='djehuty_tiqav',
      entry_points={
          'djehuty.commands': [
              'tiqav = djehuty_tiqav.commands:Tiqav',
          ],
      },
)
