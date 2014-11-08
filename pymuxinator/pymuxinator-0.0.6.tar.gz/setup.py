from setuptools import setup, find_packages

setup(
    name = "pymuxinator",
    version = "0.0.6",
    author = "Caleb Mingle",
    author_email = "caleb@mingle.cm",
    description = "Tmux session manager",
    url = "http://mingle.cm",
    packages = find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pymuxinator = pymuxinator.cli:main',
            'mux = pymuxinator.cli:start',
        ],
    },
    tests_require=[
        "nose>=1.0",
        "mock>=1.0",
    ],
    install_requires=[
        "pyyaml>=1.0",
        "Jinja2>=1.0",
    ],
    test_suite = "nose.collector"
)
