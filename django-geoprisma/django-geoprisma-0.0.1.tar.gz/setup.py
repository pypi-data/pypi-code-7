import os

from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-geoprisma',
    version='0.0.1',
    packages=find_packages(exclude=['example_project']),
    include_package_data=True,
    license='BSD License',
    description='GeoPrisma is a web mapping application',
    long_description=README,
    url='https://github.com/groupe-conseil-nutshimit-nippour/django-geoprisma',
    install_requires=[
        'Django',
        'django-modeltranslation',
        'requests',
        'lxml',
    ],
    author='Groupe Conseil Nutshimit-Nippour',
    author_email='geoprisma@gcnn.ca',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
