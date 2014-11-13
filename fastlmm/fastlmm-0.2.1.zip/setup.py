"""
file to set up python package, see http://docs.python.org/2/distutils/setupscript.html for details.
"""


import platform
import os
import sys
import shutil

from distutils.core import setup
from distutils.extension import Extension
from distutils.command.clean import clean as Clean

try:
	from Cython.Distutils import build_ext
except Exception:
	print "cython needed for installation, please install cython first"
	sys.exit()

try:
	import numpy
except Exception:
	print "numpy needed for installation, please install numpy first"
	sys.exit()


def readme():
    with open('README.md') as f:
       return f.read()


class CleanCommand(Clean):
    description = "Remove build directories, and compiled files (including .pyc)"

    def run(self):
        Clean.run(self)
        if os.path.exists('build'):
            shutil.rmtree('build')
        for dirpath, dirnames, filenames in os.walk('fastlmm'):
            for filename in filenames:
                if (filename.endswith('.so') or filename.endswith('.pyd')
                             or filename.find("wrap_plink_parser.cpp") != -1 # remove automatically generated source file
                             or filename.find("wrap_qfc.cpp") != -1 # remove automatically generated source file
                             #or filename.endswith('.dll')
                             #or filename.endswith('.pyc')
                             ):
                    tmp_fn = os.path.join(dirpath, filename)
                    print "removing", tmp_fn
                    os.unlink(tmp_fn)

# set up macro
if "win" in platform.system().lower():
    macros = [("_WIN32", "1")]
else:
    macros = [("_UNIX", "1")]

ext = [Extension("fastlmm.util.stats.quadform.qfc_src.wrap_qfc", ["fastlmm/util/stats/quadform/qfc_src/wrap_qfc.pyx", "fastlmm/util/stats/quadform/qfc_src/QFC.cpp"], language="c++",define_macros=macros)]
ext.append(Extension("pysnptools.pysnptools.snpreader.wrap_plink_parser", ["pysnptools/pysnptools/snpreader/wrap_plink_parser.pyx", "pysnptools/pysnptools/snpreader/CPlinkBedFile.cpp"], language="c++", define_macros=macros))
ext.append(Extension("pysnptools.pysnptools.snpreader.wrap_matrix_subset", ["pysnptools/pysnptools/snpreader/wrap_matrix_subset.pyx", "pysnptools/pysnptools/snpreader/MatrixSubset.cpp"], language="c++", define_macros=macros))

#python setup.py sdist bdist_wininst upload
setup(
    name='fastlmm',
    version='0.2.1',
    description='Fast GWAS',
    long_description=readme(),
    keywords='gwas bioinformatics LMMs MLMs',
    url="http://research.microsoft.com/en-us/um/redmond/projects/mscompbio/fastlmm/",
    author='MSR',
    author_email='fastlmm@microsoft.com',
    license='Apache 2.0',
    packages=[
        "fastlmm/association/tests",
        "fastlmm/association",
        "fastlmm/external/util",
        "fastlmm/external",
        "fastlmm/feature_selection",
        #"fastlmm/inference/bingpc",
        "fastlmm/inference",
        "fastlmm/pyplink/altset_list", #old snpreader
        "fastlmm/pyplink/snpreader", #old snpreader
        "fastlmm/pyplink/snpset", #old snpreader
        "fastlmm/pyplink", #old snpreader
        "fastlmm/util/runner",
        "fastlmm/util/stats/quadform",
        "fastlmm/util/standardizer",
        "fastlmm/util/stats",
        "fastlmm/util",
        "fastlmm",
        "pysnptools/pysnptools/altset_list", #new snpreader
        "pysnptools/pysnptools/snpreader", #new snpreader
        "pysnptools/pysnptools/standardizer", #new snpreader
        "pysnptools/pysnptools/util", #new snpreader
        "pysnptools/pysnptools", #new snpreader
        "pysnptools" #new snpreader
	],
	package_data={"fastlmm/association" : [
                       "Fastlmm_autoselect/FastLmmC.exe",
                       "Fastlmm_autoselect/libiomp5md.dll",
                       "Fastlmm_autoselect/fastlmmc",
                       "Fastlmm_autoselect/FastLmmC.Manual.pdf"],
                  "fastlmm/feature_selection" : [
                       "examples/bronze.txt",
                       "examples/ScanISP.Toydata.config.py",
                       "examples/ScanLMM.Toydata.config.py",
                       "examples/ScanOSP.Toydata.config.py",
                       "examples/toydata.5chrom.bed",
                       "examples/toydata.5chrom.bim",
                       "examples/toydata.5chrom.fam",
                       "examples/toydata.bed",
                       "examples/toydata.bim",
                       "examples/toydata.cov",
                       "examples/toydata.dat",
                       "examples/toydata.fam",
                       "examples/toydata.iidmajor.hdf5",
                       "examples/toydata.map",
                       "examples/toydata.phe",
                       "examples/toydata.shufflePlus.phe",
                       "examples/toydata.sim",
                       "examples/toydata.snpmajor.hdf5",
                       "examples/toydataTest.phe",
                       "examples/toydataTrain.phe"
					   ]
                 },
    requires = ['cython', 'numpy', 'scipy', 'pandas', 'sklearn', 'matplotlib'],
    #zip_safe=False,
    # extensions
    cmdclass = {'build_ext': build_ext, 'clean': CleanCommand},
    ext_modules = ext,
	include_dirs = [numpy.get_include()]
  )

