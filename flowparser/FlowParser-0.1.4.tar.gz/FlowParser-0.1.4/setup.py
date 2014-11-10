from distutils.core import setup, Extension

module = Extension('fparser', 
                    sources = ['fparser.c', 'collector.c',  
                    'dumper.c', 'logging.c', 'packer.c',
                    'parser.c',  'sniff.c'],
                    libraries = ['pcap', 'pthread'],
                    extra_compile_args = ['-Wextra', '-Werror', '-Wmissing-prototypes', '-std=gnu99', '-Wshadow', 
                                          '-Wpointer-arith', '-Wcast-qual', '-Wstrict-prototypes',
                                          '-O2', '-g3', '-Wno-missing-field-initializers'])

setup (name = 'FlowParser',
       version = '0.1.4',
       description = 'A flow parsing/dumping utility',
       ext_modules = [module],
       url = 'flowparser.googlecode.com',
       author = 'Nikola Gvozdiev',
       author_email = 'nikgvozdiev at gmail.com',
       license='MIT license',
       long_description=open('README').read())

