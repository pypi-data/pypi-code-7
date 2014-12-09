import sys


def configuration(parent_package="", top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    config.add_subpackage("tt")
    return config


def setup_package():
    build_requires = ["numpy>=1.5.1", "cython>=0.16"]
    setup_requires = build_requires
    try:
        import pip
        setup_requires = []
    except:
        pass
    install_requires = setup_requires
    metadata = {
        "name": "tt",
        "version": "0.1.1",
        "maintainer": "Iskander Sitdikov",
        "maintainer_email": "thoughteer@gmail.com",
        "description": "Support for the Tensor Train (TT) format",
        "url": "https://bitbucket.org/thoughteer/tt",
        "license": "MIT",
        "classifiers": [
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.4",
            "Topic :: Scientific/Engineering :: Mathematics",
        ],
        "setup_requires": setup_requires,
        "install_requires": install_requires,
    }
    if len(sys.argv) >= 2 and (
        "--help" in sys.argv[1:] or
        sys.argv[1] in ("--help-commands", "egg_info", "--version", "clean")
    ):
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup
    else:
        if not setup_requires:
            for package in build_requires:
                pip.main(["install", "--no-clean", package])
        if len(sys.argv) >= 2 and sys.argv[1] == "bdist_wheel":
            import setuptools
        from numpy.distutils.core import setup
        metadata["configuration"] = configuration
    setup(**metadata)


if __name__ == "__main__":
    setup_package()
