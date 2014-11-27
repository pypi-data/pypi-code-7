import os
from setuptools import setup


def read(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='django-content-toolkit',
    version='0.1.3',
    description='A simple Django package for model translations',
    long_description=(read('README.rst')),
    url='https://github.com/esistgut/django-content-toolkit',
    license='MIT',
    author='Giacomo Graziosi',
    author_email='g.graziosi@gmail.com',
    packages=['content'],
    include_package_data=True,
    install_requires=[
       'Django',
       'django-polymorphic',
       'django-reversion',
       'django-mptt',
       'django-taggit'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
