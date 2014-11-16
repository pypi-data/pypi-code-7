#!python
#-*- coding: UTF-8 -*-



import sys, os, inspect, shutil, subprocess

# this should be before any distutils command
from setuptools import setup
from setuptools import Command


from distutils.command.build import build as _build
from distutils.command.sdist import sdist as _sdist
from distutils.command import build_ext as _build_ext
from setuptools.command.install import install as _install

from distutils.command.install_lib import install_lib
from distutils import log



# OSX
# python setup.py cmake_build --boostroot=~/Code/SoftwareWorkshop/sw_thirdparties/osx/boost_1_55_patched/ --additionaloptions=-DBoost_COMPILER=-clang-darwin42


# This variable will contain the location where we can build the project. This is a temporary location pointing
# to a predefined place. This can be overridden during the installation by the build command to take the build_temp
# variable given by the user.
cmake_build_location    = os.path.join(os.path.dirname(__file__), 'build', 'tmp_cmake')

# This variable contains the location where the binaries should be installed. This is replaced during the cmake_install command
# by the final location. When set, the cmake is reconfigured, which lead to a possible relinking after a cmake_build.
cmake_install_location  = os.path.join(os.path.dirname(__file__), 'Yayi', 'bin')

# location where the cmake --build install will copy the binaries. 
cmake_install_location_cmake = os.path.join(os.path.dirname(__file__), 'Yayi', 'bin')

# This variable contains the location of the source files of Yayi. For a "sdist", the variable is used to create a proper tarball
# by copying the real repository directory into this directory.   
yayi_src_files_location = 'yayi_src_cpp'





def _utils_copy_left_to_right(root_left, left, root_right, right):
  """Simple utility functio  for copying files from a left directory to a right directory. The copy
  does not overwrite files when the corresponding file has the same time stamp. The files on the right
  are removed accordingly to reflect any change on the left.
  
  :param (string) root_left: root location of the files in the left. 
  :param (list) left: list of file names, relative to `root_left`
  :param (string) root_right: root location of the files in the right. 
  :param (list) right: list of file names, relative to `root_right`
  :returns: None
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
  
  log.warn("[YAYI] # copied files %d", nb_copied) 
  log.warn("[YAYI] # deleted (right) files %d", nb_removed) 
  log.warn("[YAYI] # replaced files %d", nb_replaced) 
    
  pass

def _utils_get_all_files(directory, no_sub_dir = False):
  """Returns all the files contained in a directory, relatively to this directory. Some files
  and extensions are ignored in the list.
  
  :param (string) directory: the directory that should be parsed
  :param (boolean) no_sub_dir: indicate if the subdirectories should be parsed as well
  :returns: a list of files relative to `directory` (`directory` is not included in the file names)
  :rtype: list
  """
  
  files_to_ignore_lower_case = ['.ds_store', '.gitignore']
  
  filter = lambda x : x.lower() not in files_to_ignore_lower_case and \
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
    
class create_sdist_layout(Command):
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
      
      # this is the restriction of the original project repository in order to create a source distribution.
      # this should be edited if something new should happen.
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
        left_file_list = _utils_get_all_files(srcdir, nosubdir)
        right_file_list = _utils_get_all_files(dstdir, nosubdir) if os.path.exists(dstdir) else []
      
        _utils_copy_left_to_right(srcdir, left_file_list, dstdir, right_file_list)

      

def cmake_configure(options):
  """Configuring CMake.
  
  This is the main function for configuring CMake on all platforms. It takes 
  """ 
  
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
           '-DCMAKE_INSTALL_PREFIX=%s' % cmake_install_location_cmake,
           # indicates that the directory part will be replaced by @rpath, related to CMAKE_INSTALL_RPATH
           '-DCMAKE_MACOSX_RPATH=ON',
           # indicates the location where the libraries will be installed after the setup install command
           '-DCMAKE_INSTALL_RPATH=%s' % os.path.abspath(install_location),
           '-DYAYI_PYTHON_PACKAGE_LOCATION=%s' % os.path.abspath(os.path.join(os.path.dirname(__file__))),
           '-DENABLE_NUMPY=True']
  
  
    # for linux
    if sys.platform == "linux2":
      for option in ["DO_NOT_USE_YAYI_JPEG", "DO_NOT_USE_YAYI_ZLIB", "DO_NOT_USE_YAYI_LIBPNG", "DO_NOT_USE_YAYI_LIBTIFF"]:
        cmd += ['-D%s=True' % option]
  
  cmd+= [cmake_path]
  
  
  log.info('#' * 40)
  log.info('# CMake configuration')
  log.info('# - command is\n\t%s\n - running in path\n\t%s', ' '.join(cmd), os.path.abspath(build_location))
  config_proc = subprocess.Popen(cmd, cwd = build_location)
  config_proc.wait()



class cmake_build(Command):
  """Calls cmake to build Yayi"""
  
  
  description = "Build of Yayi using cmake"
  user_options = [
                  ('boostroot=', None, 'specifies the boost directory'),  # option with = because it takes an argument
                  ('additionaloptions=', None, 'additional cmake options'),
                  ]
  
  def initialize_options(self):
    self.boostroot = None
    self.additionaloptions = None
    self.build_temp = None
  
  def finalize_options(self):
    self.set_undefined_options('build', ('build_temp', 'build_temp'),)
    pass
    
  def run(self):
    global cmake_build_location
    cmake_build_location = os.path.abspath(os.path.join(os.path.dirname(__file__), self.build_temp))
    
    
    log.info('#' * 40)
    log.info('[YAYI] cmake_build inside directory %s', self.build_temp)
    
    options = []
    if not self.boostroot is None:
      options += ['-DBOOST_ROOT=' + os.path.abspath(os.path.expanduser(self.boostroot))]
    
    if not self.additionaloptions is None:
      options += [self.additionaloptions]
    
    cmake_configure(options)

    # todo
    # check that the python library is compatible with the version of boost we have
    # which might be not the case for virtualenv like with exotic python +/- 
    # boost. In any case, boost-python and python should be coherent. 
    
    try:
      from multiprocessing import cpu_count
      cpu_count_ = cpu_count()
    except Exception, e:
      cpu_count_ = 1
    
    # todo flush the cmake output into a file
    build_proc = subprocess.Popen(['cmake', '--build', '.', '--', '-j%d' % cpu_count_], cwd=cmake_build_location)
    build_proc.wait()
    
    # build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'Doxygen'], cwd = cmake_build_location)
    # build_proc.wait()
    
    # build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'Sphinx'], cwd = cmake_build_location)
    # build_proc.wait()
    
    
    if(build_proc.returncode != 0):
      print '# cmake_build returned an error code', build_proc.returncode
      print '# stopping the commands'
      raise Exception('Error produced by cmake_build')

    log.info('#' * 40)
    log.info('[YAYI] cmake_build ok')
    
    
    # the installation procedure is copying yayi files into the python package tree, so it should be part of the
    # build itself
    log.info('#' * 40)
    log.info('[YAYI] cmake_build -- install')

    build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'install'], cwd=cmake_build_location)
    build_proc.wait()
  
    if(build_proc.returncode != 0):
      log.error('[YAYI] cmake_build install returned an error code %d', build_proc.returncode)
      log.error('[YAYI] stopping the commands')
      raise Exception('Error produced by cmake_install, see logs for more information')    

    log.info('#' * 40)
    log.info('[YAYI] cmake_build -- install ok')

  def get_outputs(self):
    """Returns the list of files generated by this specific build command"""
    # Apparently needed while undocumented. Note: should be able to run it in dry-run, which is now impossible
    log.warn('#' * 40 + " I am in get_outputs" )
    out_files = _utils_get_all_files(cmake_install_location_cmake)
    log.warn("returning %s", out_files) 
    return out_files




class cmake_install(Command):
  """Wrapper around the `make install` command of cmake"""
  
  description = "Yayi installation through cmake"

  
  def initialize_options(self):
    self.prefix = None
    #self.install_lib = None
    #self.install_platlib = None
    pass
    
  def finalize_options(self):
    self.set_undefined_options('install',
                               ('prefix', 'prefix'),
                               #('install_lib', 'install_lib'),
                               #('install_platlib', 'install_platlib'),
                               )      
    
  def run(self):
    log.info('#' * 40)
    log.info('[YAYI] cmake_install (using prefix %s)', self.prefix)
    
    build_proc = subprocess.Popen(['cmake', '--build', '.', '--', 'install'], cwd=cmake_build_location)
    build_proc.wait()
  
    if(build_proc.returncode != 0):
      log.error('[YAYI] cmake_install returned an error code %d', build_proc.returncode)
      log.error('[YAYI] stopping the commands')
      raise Exception('Error produced by cmake_install, see logs for more information')

    log.info('#' * 40)
    log.info('[YAYI] cmake_install ok', self.prefix)



#############################################
#
# Overrides of the regular distutils commands
# Needed in order to perform the commands in the right order and to capture
# some variables needed during the builds.

class build(_build):
  # cmake_build should appear as the first command, otherwise wrong rpath libraries will be copied in
  # the intermediate build/ directory
  sub_commands = [('create_sdist_layout', None), ('cmake_build', None)] + _build.sub_commands

class install(_install):
  """Modified installation that fills the prefix installation in a global variable for the cmake
     and adds the necessary cmake_install subcommands as a dependency."""
     
  # build should be there in order to ensure that, if a new prefix is given, the the binaries are
  # built with the correct rpath stuff.
  # sub_commands = [('cmake_install', None)] + _install.sub_commands

 
  def run(self):
    global cmake_install_location
    cmake_install_location = os.path.join(self.install_lib, 'Yayi', 'bin')
    log.info('#' * 40)
    log.info('[YAYI] cmake installation location is %s', cmake_install_location)
    
    _install.run(self)

class sdist(_sdist):
  """Modified source distribution that installs create_sdist_layout as a dependant subcommand"""
  sub_commands = [('create_sdist_layout', None)] + _sdist.sub_commands
  
  def get_file_list(self):
    """Extends the file list read from the manifest with the sources of Yayi"""
    
    _sdist.get_file_list(self)
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), yayi_src_files_location))
    my_files = _utils_get_all_files(src_dir)
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

cmdclass= { 'build': build,
            'cmake_build': cmake_build,
            'cmake_install': cmake_install,
            'install': install,
            'sdist': sdist,
            'create_sdist_layout': create_sdist_layout
           }

setup(
  name          = 'Yayi',
  version       = '0.8.5dev',
  
  author        = 'Raffi Enficiaud',
  author_email  = 'raffi.enficiaud@free.fr',
  
  url           = 'http://raffi.enficiaud.free.fr',
  packages      = ['Yayi', 'Yayi.extensions', 'Yayi.tests'],
  package_data  = { 'Yayi': ['bin/*.*'] },
  classifiers   = classifiers,
  keywords      = keywords,
  license       ='Boost Software License - Version 1.0 - August 17th, 2003',
  description   = 'Yayi toolbox for image processing and mathematical morphology',
  long_description=open('README.txt').read(),
  cmdclass      = cmdclass,
)

