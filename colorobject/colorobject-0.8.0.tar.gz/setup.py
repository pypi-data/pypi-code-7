from setuptools import setup

try:
    import matplotlib
except ImportError:
    raise ImportError("Please install matplotlib")

setup(
      name         = 'colorobject',
      packages     = ['colorobject'],
      version      = '0.8.0',
      description  = 'Dynamic color objects compatible with Matplotlib',
      author       = 'Gen Del Raye',
      author_email = 'gdelraye@hawaii.edu',
      url          = '',
      download_url = '',
      keywords     = ['matplotlib', 'color', 'hls', 'hsv', 'color name', 'colormap'],
      install_requires = [],
      package_data = {},
      classifiers  = [
                      "Intended Audience :: Science/Research",
                      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                      "Natural Language :: English",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python",
                      "Topic :: Scientific/Engineering",
                      "Development Status :: 4 - Beta"],
      )