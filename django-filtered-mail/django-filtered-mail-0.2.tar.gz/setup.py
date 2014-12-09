from setuptools import setup, find_packages

import os

def get_long_description():
    path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(path) as f:
        return f.read()

setup(
    name='django-filtered-mail',
    version="0.2",
    packages=find_packages(),
    author='Rudolph Froger',
    author_email='rudolphfroger@dreamsolution.nl',
    license='MIT',
    description='Django Email Backend which only sends to whitelisted recipients',
    long_description=get_long_description(),
    url='https://github.com/rudolphfroger/django-filtered-mail',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.6',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Communications :: Email :: Filters',
    ],
)
