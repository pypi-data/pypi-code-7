#!/usr/bin/env python3

""" Sanzang Lib setup script for packaging and installation. """

from distutils.core import setup

with open('README.rest', 'r', encoding='utf-8') as fin:
    LONG_DESCRIPTION = fin.read()

setup(
    #
    # Basic information
    #
    name='sanzang-lib',
    version='1.0.1',
    author='yaoguai',
    author_email='lapislazulitexts@gmail.com',
    url='https://github.com/yaoguai/sanzang-lib',
    license='MIT',
    #
    # Descriptions & classifiers
    #
    description='Translate from Chinese, Japanese, or Korean.',
    long_description=LONG_DESCRIPTION,
    keywords='chinese japanese korean cjk asia language translation',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Religion',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic'],
    #
    # Included Python files
    #
    py_modules=['sanzang'],
    data_files=[
        ('share/doc/sanzang-lib', [
            'AUTHORS.rest',
            'LICENSE.rest',
            'NEWS.rest',
            'README.rest'])]
)
