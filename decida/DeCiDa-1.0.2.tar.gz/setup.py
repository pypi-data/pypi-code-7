from distutils.core import setup
import os.path

DECIDA_HOME = os.path.expanduser("~/.DeCiDa")

setup(
    name='DeCiDa',
    version='1.0.2',
    author='Richard Booth',
    author_email='rvb2@lehigh.edu',
    packages=['decida', 'decida.test'],
    package_data={
        "decida": ["dataview_help/*", "twin_help/*", "plotter_help/*"],
        "decida.test": ["*.raw", "*.ckt", "*.net", "*.v", "*.txt", "*.report", "*.data", "*.csv", "*.col", "*.ssv"],
    },
    scripts=[
        'bin/calc',
        'bin/dataview',
        'bin/gifimg',
        'bin/ngsp',
        'bin/op',
        'bin/pll_phase_noise',
        'bin/pllss',
        'bin/plotter',
        'bin/simvision_csv2col',
        'bin/twin',
    ],
    data_files=[
        (DECIDA_HOME + '/dot', [
               'etc/dot/.cdsinit',
               'etc/dot/.oceanrc',
               'etc/dot/.pythonrc.py',
           ]
        ),
        (DECIDA_HOME + '/lib', [
               'etc/lib/README',
           ]
        ),
        (DECIDA_HOME + '/projects/bird', [
               'etc/projects/bird/README',
           ]
        ),
        (DECIDA_HOME + '/projects/bird/scratch', [
               'etc/projects/bird/scratch/README',
           ]
        ),
        (DECIDA_HOME + '/projects/trane', [
               'etc/projects/trane/README',
           ]
        ),
        (DECIDA_HOME + '/projects/trane/scratch', [
               'etc/projects/trane/scratch/README',
           ]
        ),
        (DECIDA_HOME + '/stdcell/ptm_130nm', [
               'etc/stdcell/ptm_130nm/README',
               'etc/stdcell/ptm_130nm/LICENSE',
               'etc/stdcell/ptm_130nm/NangateOpenCellLibrary.v',
           ]
        ),
        (DECIDA_HOME + '/stdcell/ptm_45nm', [
               'etc/stdcell/ptm_45nm/README',
               'etc/stdcell/ptm_45nm/LICENSE',
               'etc/stdcell/ptm_45nm/NangateOpenCellLibrary.v',
           ]
        ),
        (DECIDA_HOME + '/bin', [
               'etc/wrappers/run_hspice',
               'etc/wrappers/run_ngspice',
               'etc/wrappers/run_spectre',
               'etc/wrappers/run_sspice',
           ]
        ),
        (DECIDA_HOME + '/models', [
               'etc/models/ptm_130nm.lib',
               'etc/models/ptm_130nm.scs',
               'etc/models/ptm_130nm_mos.inc',
               'etc/models/ptm_130nm_mos.scs',
               'etc/models/ptm_45nm.lib',
               'etc/models/ptm_45nm.scs',
               'etc/models/ptm_45nm_mos.inc',
               'etc/models/ptm_45nm_mos.scs',
           ]
        ),
        (DECIDA_HOME + '/skill', [
               'etc/skill/RVBcomp.il',
               'etc/skill/RVBdcd_help.txt',
               'etc/skill/RVBdcdlines.il',
               'etc/skill/RVBmenu.il',
               'etc/skill/RVButil.il',
               'etc/skill/RVBvtb_help.txt',
               'etc/skill/RVBvtblines.il',
           ]
        ),
        (DECIDA_HOME + '/verilog', [
               'etc/verilog/Makefile',
               'etc/verilog/make.bird',
               'etc/verilog/make.trane',
               'etc/verilog/make_body',
               'etc/verilog/simvision_core.tcl',
           ]
        ),
        (DECIDA_HOME + '/cython', [
               'etc/cython/setup_data.py',
               'etc/cython/setup_xyplotx.py',
           ]
        ),
    ],
    url='http://pypi.python.org/pypi/DeCiDa/',
    license='LICENSE.txt',
    description='Device and Circuit Data Analysis',
    long_description=open('README.txt').read(),
    platforms=["Linux", "MacOS", "CygWin", "Windows"],
    classifiers = [
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Multimedia :: Graphics',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
            'Topic :: Scientific/Engineering :: Visualization',
    ]
)
