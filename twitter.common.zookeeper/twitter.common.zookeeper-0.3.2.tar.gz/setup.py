
# DO NOT EDIT THIS FILE -- AUTOGENERATED BY PANTS
# Target: PythonLibrary(BuildFileAddress(/Users/zmanji/workspace/commons/src/python/twitter/common/zookeeper/BUILD, zookeeper))

from setuptools import setup

setup(**
{   'description': "Implementations of Twitter's service discovery libraries on top of Kazoo.",
    'extras_require': {   'old': ['zc-zookeeper-static==3.4.4']},
    'install_requires': [   'kazoo==1.3.1',
                            'thrift==0.9.1',
                            'twitter.common.concurrent==0.3.2',
                            'twitter.common.log==0.3.2',
                            'twitter.common.metrics==0.3.2'],
    'name': 'twitter.common.zookeeper',
    'namespace_packages': [   'gen',
                              'gen.twitter',
                              'gen.twitter.thrift',
                              'twitter',
                              'twitter.common'],
    'package_data': {   },
    'package_dir': {   '': 'src'},
    'packages': [   '.',
                    'gen',
                    'gen.twitter',
                    'gen.twitter.thrift',
                    'gen.twitter.thrift.endpoint',
                    'twitter',
                    'twitter.common',
                    'twitter.common.zookeeper',
                    'twitter.common.zookeeper.group',
                    'twitter.common.zookeeper.serverset'],
    'version': '0.3.2'}
)
