from setuptools import setup

try:
    import matplotlib
except ImportError:
    raise ImportError("Please install matplotlib")

setup(
      name         = 'plotsettings',
      packages     = ['plotsettings'],
      version      = '1.0.4-2',
      description  = 'Easily format figures to match the publication requirements of an academic journal',
      author       = 'Gen Del Raye',
      author_email = 'gdelraye@hawaii.edu',
      url          = '',
      download_url = '',
      keywords     = ['matplotlib', 'rcParams', 'journal', 'figure size', 'plot settings', 'panel labels'],
      install_requires = [],
      package_data = {'plotsettings': ['test/*.py']},
      classifiers  = [
                      "Intended Audience :: Science/Research",
                      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                      "Natural Language :: English",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python",
                      "Topic :: Scientific/Engineering",
                      "Development Status :: 4 - Beta"],
      )