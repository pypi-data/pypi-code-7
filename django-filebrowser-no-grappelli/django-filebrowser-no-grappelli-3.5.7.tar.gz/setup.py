import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-filebrowser-no-grappelli',
    version='3.5.7',
    description='Media-Management no Grappelli',
    long_description = read('README.rst'),
    url = 'https://github.com/smacker/django-filebrowser-no-grappelli',
    download_url='',
    author='Patrick Kranzlmueller, Axel Swoboda (vonautomatisch)',
    author_email='office@vonautomatisch.at',
    maintainer='Maxim Sukharev',
    maintainer_email='max@smacker.ru',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    zip_safe = False
)
