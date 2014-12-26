from distutils.core import setup

with open('README.rst') as readme:
    long_description = readme.read()

setup(name='django-numfilters',
      version='0.1.1',
      description='Mathematical template filters for Django',
      long_description=long_description,
      author='Adrian Matellanes',
      author_email='matellanesadrian@gmail.com',
      url='https://github.com/amatellanes/django-numfilters',
      license='MIT',
      keywords='django number math template filters',
      packages=['django_numfilters', 'django_numfilters.templatetags'],
      package_dir={'django_numfilters': 'django_numfilters'},
      platforms=['any'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Utilities'
      ],
)