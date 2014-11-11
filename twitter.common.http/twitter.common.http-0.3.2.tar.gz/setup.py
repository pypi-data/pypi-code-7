
# DO NOT EDIT THIS FILE -- AUTOGENERATED BY PANTS
# Target: PythonLibrary(BuildFileAddress(/Users/zmanji/workspace/commons/src/python/twitter/common/http/BUILD, http))

from setuptools import setup

setup(**
{   'classifiers': [   'Intended Audience :: Developers',
                       'License :: OSI Approved :: Apache Software License',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python'],
    'description': 'twitter.common wrappers for bottle and simple diagnostics endpoints.',
    'install_requires': ['bottle==0.11.6', 'twitter.common.log==0.3.2'],
    'license': 'Apache License, Version 2.0',
    'name': 'twitter.common.http',
    'namespace_packages': ['twitter', 'twitter.common'],
    'package_data': {   },
    'package_dir': {   '': 'src'},
    'packages': ['twitter', 'twitter.common', 'twitter.common.http'],
    'url': 'https://github.com/twitter/commons',
    'version': '0.3.2',
    'zip_safe': True}
)
