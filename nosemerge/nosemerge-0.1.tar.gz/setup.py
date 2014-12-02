from setuptools import setup, find_packages
setup(
    name = "nosemerge",
    version = "0.1",
    packages = find_packages(),
    scripts = ['nosemerge.py'],

    install_requires = [],
  

    package_data = {
        '': ['*.ini', '*.txt'],
    },

    # metadata for upload to PyPI
    author = "Sergey Melekhin",
    author_email = "cpro29a@gmail.com",
    description = "Simple nosetests xml report merge tool",
    license = "LGPL",
    keywords = "xml unittest nose nosetests",
    url = "https://github.com/C-Pro/nosemerge",
    download_url = "https://github.com/C-Pro/nosemerge/tarball/0.1",

)