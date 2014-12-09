import os
import cked
from setuptools import setup, find_packages


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='twentytab-cked',
    version=cked.__version__,
    author='20tab srl',
    author_email='info@20tab.com',
    description=('CKEditor and elFinder integration for Django Framework.'),
    license='BSD',
    keywords='django, ckeditor, elfinder, wysiwyg, upload',
    url='https://github.com/20tab/twentytab-cked',
    long_description=read('README.rst'),
    install_requires=[
        'Django >=1.6',
        'django-appconf>=0.6',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
    }
)
