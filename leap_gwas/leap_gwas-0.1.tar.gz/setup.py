"""
file to set up python package, see http://docs.python.org/2/distutils/setupscript.html for details.
"""


import platform
import os
import sys
import shutil
import setuptools

from distutils.core import setup
from distutils.extension import Extension
from distutils.command.clean import clean as Clean


try: import numpy	
except Exception:
	print "numpy needed for installation, please install numpy first"
	sys.exit()
try: import scipy
except Exception:
	print "scipy needed for installation, please install numpy first"
	sys.exit()

def readme():
    with open('LEAP/README.md') as f:
       return f.read()


class CleanCommand(Clean):
    description = "Remove build directories, and compiled files (including .pyc)"

    def run(self):
        Clean.run(self)
        if os.path.exists('build'):
            shutil.rmtree('build')
            for dirpath, dirnames, filenames in os.walk('.'):
                for filename in filenames:
                    if (filename.endswith('.so') or filename.endswith('.pyd')):
                        tmp_fn = os.path.join(dirpath, filename)
                        print "removing", tmp_fn
                        os.unlink(tmp_fn)

# set up macro
if "win" in platform.system().lower():
    macros = [("_WIN32", "1")]
else:
    macros = [("_UNIX", "1")]


#python setup.py sdist bdist_wininst upload
setup(
    name='leap_gwas',
    version='0.1',
    description='Liability Estimation in Case Control Studies',
    long_description=readme(),
    keywords='gwas bioinformatics LMMs MLMs',
    url="https://github.com/omerwe/LEAP",
    author='Omer Weissbrod',
    author_email='omerw@cs.technion.ac.il',
    license='Apache 2.0',    
	packages=["LEAP"],
    include_package_data=True,
	package_data={
		"LEAP" : ["README.MD", "LICENSE.MD", "leap_pipeline.sh"],
					   # "dataset1" : [
                       # "dataset1/dataset1.phe.liab",
                       # "dataset1/dataset1.phe",
					   # "dataset1/dataset1.fam",
					   # "dataset1/dataset1.bim",
					   # "dataset1/dataset1.bed",
					   # "dataset1/dataset1.cov",
					   # "dataset1/extracts/chr1_extract.txt",
					   # "dataset1/extracts/nochr1_extract.txt",
					   # "dataset1/extracts/chr2_extract.txt",
					   # "dataset1/extracts/nochr2_extract.txt",
					   # "dataset1/extracts/chr3_extract.txt",
					   # "dataset1/extracts/nochr3_extract.txt",
					   # "dataset1/extracts/chr4_extract.txt",
					   # "dataset1/extracts/nochr4_extract.txt",
					   # "dataset1/extracts/chr5_extract.txt",
					   # "dataset1/extracts/nochr5_extract.txt",
					   # "dataset1/extracts/chr6_extract.txt",
					   # "dataset1/extracts/nochr6_extract.txt",
					   # "dataset1/extracts/chr7_extract.txt",
					   # "dataset1/extracts/nochr7_extract.txt",
					   # "dataset1/extracts/chr8_extract.txt",
					   # "dataset1/extracts/nochr8_extract.txt",
					   # "dataset1/extracts/chr9_extract.txt",
					   # "dataset1/extracts/nochr9_extract.txt",
					   # "dataset1/extracts/chr10_extract.txt",
					   # "dataset1/extracts/nochr10_extract.txt"
					   # ]
                },
    requires = ['numpy', 'scipy', 'fastlmm', 'sklearn'],
    #zip_safe=False,
    # extensions        
	include_dirs = [numpy.get_include()]
  )	   
	
