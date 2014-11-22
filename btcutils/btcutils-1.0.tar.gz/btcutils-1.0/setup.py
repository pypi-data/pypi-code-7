from distutils.core import setup, Extension
import os

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"

module1 = Extension('btcutils',
                    sources = [
                        'uint256.cpp',
                        'utilstrencodings.cpp',
                        'sha2.cpp',
                        'main.cpp',
                        ],
                     language = "c++")
setup (name = 'btcutils',
       version = '1.0',
       description = 'Python native extension providing Bitcoin related functions',
       ext_modules = [module1])
