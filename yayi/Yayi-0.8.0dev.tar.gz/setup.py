#!python
#-*- coding: UTF-8 -*-

# python setup.py build

import sys, os, inspect, shutil

from setuptools import setup


from distutils.command.build import build as _build
from distutils.command.sdist import sdist as _sdist
from distutils.command import build_ext as _build_ext
from setuptools import Command
from setuptools.command.install import install as _install

import distutils.dir_util as dd

from setuptools.extension import Extension

from distutils import log
from distutils.command.sdist import sdist

# OSX
# python setup.py cmake_build --boostroot=~/Code/SoftwareWorkshop/sw_thirdparties/osx/boost_1_55_patched/ --additionaloptions=-DBoost_COMPILER=-clang-darwin42


cmake_build_location    = os.path.join(os.path.dirname(__file__), 'build', 'tmp_cmake')
cmake_install_location  = os.path.join(os.path.dirname(__file__), 'Yayi', 'bin')

yayi_src_files_location = 'yayi_src_cpp'

import subprocess 


def copy_left_to_right(root_left, left, root_right, right):
  """
  
  :param (list) left: list of file names, relative to root_left
  """
  from stat import ST_MTIME
  
  keep_file = lambda x, y:  os.path.exists(os.path.join(y, x)) and os.path.isfile(os.path.join(y, x))
  
  # keep only existing ones and files
  set_left = set((i for i in left if keep_file(i, root_left))) 
  set_right= set((i for i in right if keep_file(i, root_right)))
  left_only =  set_left - set_right
  right_only = set_right - set_left
  
  # removing right only, checking consistency first
  for f in right_only:
    file_to_remove = os.path.join(root_right, f)
    assert(os.path.exists(file_to_remove))
  
  nb_removed = 0
  for f in right_only:
    os.remove(os.path.join(root_right, f))
    nb_removed += 1
  
  # copying left only
  nb_copied = 0
  for f in left_only:
    destination = os.path.join(root_right, f)
    dirname = os.path.dirname(destination)
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    
    shutil.copyfile(os.path.join(root_left, f), destination)
    nb_copied += 1
  
  
  # for the others, check the date
  nb_replaced = 0
  for f in set_left & set_right:
    src = os.path.join(root_left, f)
    dst = os.path.join(root_right, f)
    
    if os.stat(src)[ST_MTIME] > os.stat(dst)[ST_MTIME]:
      shutil.copyfile(src, dst)
      nb_replaced += 1
  
  print "# nb copied files", nb_copied 
  print "# nb deleted (right) files", nb_removed 
  print "# nb replaced files", nb_replaced 
    
  pass

def get_all_files(directory, no_sub_dir = False):
  filter = lambda x : x.lower() != '.ds_store' and \
                      os.path.splitext(x)[1].lower() != '.bak' and \
                      x.find('~') == -1
  file_list = []
  for root, dirlist, filelist in os.walk(directory, True):
    file_list += [os.path.join(root, f) for f in filelist if filter(f)]
    if no_sub_dir:
      break
  
  file_list = [os.path.abspath(f) for f in file_list]
  file_list = [os.path.relpath(f, os.path.abspath(directory)) for f in file_list]
  return file_list
    
class yayi_src_layout(Command):
    description = "Copy the necessary files from the repository layout for making a proper distribution layout"
    user_options = [
        ('from-original-repository', None, "Set to true for original repository setup")
    ]

    def initialize_options(self):
      pass
    
    def finalize_options(self):
      pass

    def run(self):
      
      destination_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), yayi_src_files_location))
      if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
      original_repository_base_directory = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
      
      paths_to_copy = (('.', True),
                       ('cmake', False), 
                       ('core', False),
                       ('doc', False),
                       ('coreTests', False), # remove the data directory here
                       ('python', False),
                       ('plugins/external_libraries', False))

      # check if we are in our repository configuration
      for current_root, nosubdir in paths_to_copy:
        if not os.path.exists(os.path.join(original_repository_base_directory, current_root)):
          return
      
      for current_root, nosubdir in paths_to_copy:        
        srcdir = os.path.join(original_repository_base_directory, current_root)
        dstdir = os.path.join(destination_directory, current_root)
        left_file_list = get_all_files(srcdir, nosubdir)
        right_file_list = get_all_files(dstdir, nosubdir) if os.path.exists(dstdir) else []
      
        copy_left_to_right(srcdir, left_file_list, dstdir, right_file_list)

      

def configure_cmake(options):
  
  
  # cmake location
  yayi_root_path = yayi_src_files_location
  
  
  # build location
  build_location = cmake_build_location
  if not os.path.exists(build_location):
    os.makedirs(build_location)
    
  # relative cmake path
  cmake_path = os.path.relpath(yayi_root_path, os.path.abspath(build_location))
  
  
  cmd = ['cmake']
  cmd+= options
  
  install_location = cmake_install_location
  if(not install_location is None):
    
    # this is the commands for OSX.
    # this looks to work properly on a boost version that was installed with brew. The boost binaries
    # should have their soname set properly (full path) otherwise DYLD_LIBRARY_PATH is required at runtime 
    cmd+= [# directory where we will install the libraries
           '-DCMAKE_INSTALL_PREFIX=%s' % os.path.abspath(os.path.join(os.path.dirname(__file__), 'Yayi', 'bin')),
           # indicates that the directory part will be replaced by @rpath, related to CMAKE_INSTALL_RPATH
           '-DCMAKE_MACOSX_RPATH=ON',
           # indicates the location where the libraries will be installed after the setup install command
           '-DCMAKE_INSTALL_RPATH=%s' % os.path.abspath(install_location),
           '-DYAYI_PYTHON_PACKAGE_LOCATION=%s' % os.path.abspath(os.path.join(os.path.dirname(__file__)))]
  
  cmd+= [cmake_path]
  
  
  print 'Configuring'
  print 'cmake command is', cmd, 'running in path', os.path.abspath(build_location)
  config_proc = subprocess.Popen(cmd, cwd = build_location)
  config_proc.wait()



class cmake_build(Command):
    description = "Cmake build of Yayi"
    user_options = [
                    ('boostroot=', None, 'specifies the boost directory'), # option with = because it takes an argument
                    ('additionaloptions=', None, 'additional cmake options'),
                    ]
    
    def initialize_options(self):
        self.boostroot = None
        self.additionaloptions = None
        self.build_temp = None
    
    def finalize_options(self):
      self.set_undefined_options('build', ('build_temp', 'build_temp'), )      
      
      pass
      
    def run(self):
      global cmake_build_location
      cmake_build_location = os.path.abspath(os.path.join(os.path.dirname(__file__), self.build_temp))
      
      print '#' * 40
      print '# cmake_build'
      print '# building inside directory', self.build_temp
      #raw_input('cmake_build custom')
                
      options = []
      if not self.boostroot is None:
        options += ['-DBOOST_ROOT=' + os.path.abspath(os.path.expanduser(self.boostroot))]
      
      if not self.additionaloptions is None:
        options += [self.additionaloptions]
      
      configure_cmake(options)

      # todo
      # check that the python library is compatible with the version of boost we have
      # which might be not the case for virtualenv like with exotic python +/- 
      # boost. In any case, boost-python and python should be coherent. 
      
      print 'Building yayi with cmake ...'
      try:
        from multiprocessing import cpu_count
        cpu_count_ = cpu_count()
      except Exception, e:
        cpu_count_ = 1
      
      # todo flush the cmake output into a file
      build_proc = subprocess.Popen(['cmake', '--build', '.', '--', '-j%d' % cpu_count_], cwd = cmake_build_location)
      build_proc.wait()
      
      #build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'Doxygen'], cwd = cmake_build_location)
      #build_proc.wait()
      
      #build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'Sphinx'], cwd = cmake_build_location)
      #build_proc.wait()
      
      print '#' * 40
      print '# cmake_build exit'
      
      if(build_proc.returncode != 0):
        print '# cmake_build returned an error code', build_proc.returncode
        print '# stopping the commands'
        raise Exception('Error produced by cmake_build')


class cmake_install(Command):
    description = "This is a wrapper around the cmake installation for Yayi"

    
    def initialize_options(self):
        self.prefix = None
        self.install_lib = None
        self.install_platlib = None
        pass
      
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('prefix', 'prefix'),
                                   ('install_lib', 'install_lib'),
                                   ('install_platlib', 'install_platlib'),)      
      
    def run(self):
      print '#' * 40
      print 'cmake_install'
      
      print 'installation prefix', self.prefix
      #print 'self.install_lib', self.install_lib
      #print 'self.install_platlib', self.install_platlib
      #raw_input("cmake install")
      
      build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'install'], cwd = cmake_build_location)
      build_proc.wait()

      print '#' * 40
      print 'cmake_install exit'
        
      if(build_proc.returncode != 0):
        print '# cmake_install returned an error code', build_proc.returncode
        print '# stopping the commands'
        raise Exception('Error produced by cmake_install')

class build(_build):
  # cmake_build should appear as the first command, otherwise wrong rpath libraries will be copied in
  # the intermediate build/ directory
  sub_commands = [('yayi_src_layout', None), ('cmake_build', None)] + _build.sub_commands


class install(_install):
  """Modified installation that fills the prefix installation in a global variable for the cmake
     and adds the necessary cmake_install subcommands as a dependency."""
  sub_commands = [('build', None)] + _install.sub_commands
  
 
  def run(self):
    global cmake_install_location
    cmake_install_location = os.path.join(self.install_lib, 'Yayi', 'bin')
    
    print '#' * 40
    print 'install'
    
    _install.run(self)


class sdist(_sdist):
  """Modified source distribution that installs yayi_src_layout as a dependant subcommand"""
  sub_commands = [('yayi_src_layout', None)] + _sdist.sub_commands
  
  def get_file_list(self):
    """Extends the file list read from the manifest with the sources of Yayi"""
    
    _sdist.get_file_list(self)
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), yayi_src_files_location))
    my_files = get_all_files(src_dir)
    my_files = [os.path.join(src_dir, x) for x in my_files]
    my_files = [os.path.relpath(x, os.path.abspath(os.path.dirname(__file__))) for x in my_files]
    self.filelist.extend(my_files)
    return
    

classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Developers',
  'Intended Audience :: Information Technology',
  'Intended Audience :: Science/Research',
  'Operating System :: MacOS :: MacOS X',
  'Operating System :: Microsoft :: Windows :: Windows NT/2000',
  'Operating System :: POSIX :: Linux',
  'Programming Language :: C++',
  'Programming Language :: Python :: 2.7',
  'Topic :: Scientific/Engineering :: Image Recognition',
  'Topic :: Scientific/Engineering :: Mathematics',
]

keywords = 'image processing', 'mathematical morphology', \
           'multidimensional images', 'multispectral images', \
           'image segmentation', 'erosion', 'dilation', \
           'opening', 'closing', 'hit-or-miss', 'connected components' 



b = setup(
      name          = 'Yayi',
      version       = '0.8.0dev',
      
      author        = 'Raffi Enficiaud',
      author_email  = 'raffi.enficiaud@free.fr',
      
      url           = 'http://raffi.enficiaud.free.fr',
      packages      = ['Yayi',],
      package_data  = { 'Yayi': ['bin/*.*'] },
      classifiers   = classifiers,
      keywords      = keywords,
      license       ='Boost Software License - Version 1.0 - August 17th, 2003',
      description   = 'Yayi toolbox for image processing and mathematical morphology',
      long_description=open('README.txt').read(),

      cmdclass={'build': build,
                'cmake_build': cmake_build,
                'cmake_install': cmake_install,
                'install': install,
                'sdist': sdist,
                'yayi_src_layout': yayi_src_layout
                }

     )

