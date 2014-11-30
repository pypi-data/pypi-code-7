import os
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-console',
    description='bash console in the browser for django admins',
    keywords='django, bash',
    packages=find_packages(),
    include_package_data=True,
    version="0.4.6",
    author="Anoop Thomas Mathew",
    author_email="atmb4u@gmail.com",
    classifiers=['Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license="BSD License",
    platforms=["all"],
    zip_safe=False
)


# # -*- coding: utf-8 -*-
# __author__ = 'atm'
# from setuptools import setup
# import os
# packages = []
# data_files = []
#
#
# def fullsplit(path, result=None):
#     if result is None:
#         result = []
#         head, tail = os.path.split(path)
#     if head == '':
#         return [tail] + result
#     if head == path:
#         return result
#     return fullsplit(head, [tail] + result)
#
#
# SKIP_EXTENSIONS = ['.pyc', '.pyo', '.swp', '.swo']
#
#
# def is_unwanted_file(filename):
#     for skip_ext in SKIP_EXTENSIONS:
#         if filename.endswith(skip_ext):
#             return True
#         return False
#
# for dirpath, dirnames, filenames in os.walk("django-console"):
#     for i, dirname in enumerate(dirnames):
#         if dirname.startswith('.'):
#             del dirnames[i]
#     for filename in filenames:
#         if filename.endswith('.py'):
#             packages.append('.'.join(fullsplit(dirpath)))
#         elif is_unwanted_file(filename):
#             pass
#         else:
#             data_files.append(
#                 [dirpath, [os.path.join(dirpath, f) for f in filenames]],
#             )
#
# setup(
#     name='django-console',
#     version='0.4.4',
#     author=u'Anoop Thomas Mathew',
#     author_email='atmb4u@gmail.com',
#     packages=['django-console'],
#     url='http://github.com/atmb4u/django-console',
#     license='BSD License, see LICENSE',
#     description='bash console in the browser for django admins',
#     zip_safe=False,
#     data_files=data_files
# )
